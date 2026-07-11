#!/usr/bin/env python3
"""Audit official Queensland dam EAP documents and build a machine-readable cache.

This is deliberately separate from the hourly storage collector. EAP PDFs are large,
change infrequently, and require conservative parsing. The job discovers official
links, records document metadata/hash, extracts the activation quick-reference text,
and applies manually verified flood-operation rules where available.

Machine-extracted rules are clearly labelled and are never represented as an
operator's formal activation status.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import logging
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
from pypdf import PdfReader
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config"
DATA = ROOT / "data"
DIRECTORY_URL = "https://www.business.qld.gov.au/industries/mining-energy-water/water/industry-infrastructure/dams/referable-dam-eaps"
SUNWATER_EAP_INDEX = "https://www.sunwater.com.au/community/preparing-for-emergencies/emergency-management/"
USER_AGENT = "QueenslandDamDashboard-EAP-Audit/1.0 (+https://github.com/gowlettluke/qlddams)"
LOG = logging.getLogger("eap-audit")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return copy.deepcopy(default)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def norm(value: Any) -> str:
    text = unicodedata.normalize("NFKD", clean(value)).encode("ascii", "ignore").decode().lower()
    text = text.replace("macdonald", "macdonald").replace("e.j.", "ej")
    return re.sub(r"[^a-z0-9]", "", text)


def make_session() -> requests.Session:
    retry = Retry(total=3, connect=3, read=3, backoff_factor=1.2,
                  status_forcelist=(429, 500, 502, 503, 504), allowed_methods=frozenset(("GET",)))
    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept-Language": "en-AU,en;q=0.9",
        "Accept": "text/html,application/pdf,application/xhtml+xml,*/*;q=0.8",
    })
    session.mount("https://", HTTPAdapter(max_retries=retry, pool_connections=8, pool_maxsize=8))
    return session


def discover_directory_links(session: requests.Session, sources: list[dict[str, Any]]) -> dict[str, dict[str, str]]:
    response = session.get(DIRECTORY_URL, timeout=60)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    anchors = []
    for a in soup.find_all("a", href=True):
        label = clean(a.get_text(" ", strip=True))
        href = urljoin(DIRECTORY_URL, a["href"])
        context = clean(a.parent.get_text(" ", strip=True) if a.parent else label)
        anchors.append((norm(label), norm(context), label, href))

    output: dict[str, dict[str, str]] = {}
    for source in sources:
        if not source.get("referable", True):
            continue
        wanted = norm(source.get("directory_name"))
        candidates = []
        for label_key, context_key, label, href in anchors:
            if wanted and (wanted in label_key or wanted in context_key):
                score = 0
                if wanted in label_key:
                    score += 100
                if "eap" in label_key or href.lower().endswith(".pdf"):
                    score += 40
                if "emergencyinformation" in label_key or "emergencyinformation" in context_key:
                    score += 20
                candidates.append((score, label, href))
        eap = next((href for score, label, href in sorted(candidates, reverse=True)
                    if "eap" in label.lower() or href.lower().endswith(".pdf")), None)
        info = next((href for score, label, href in sorted(candidates, reverse=True)
                     if "emergency information" in label.lower() and not href.lower().endswith(".pdf")), None)
        output[source["dam_id"]] = {"eap_url": eap, "emergency_info_url": info}
    return output


def discover_sunwater_links(session: requests.Session, sources: list[dict[str, Any]]) -> dict[str, dict[str, str]]:
    """Operator-page fallback when a government-directory PDF link has moved."""
    response = session.get(SUNWATER_EAP_INDEX, timeout=60)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    output: dict[str, dict[str, str]] = {}
    for source in (x for x in sources if x.get("operator") == "Sunwater"):
        wanted = norm(source.get("directory_name"))
        heading = None
        for h in soup.find_all(["h2", "h3", "h4", "h5"]):
            if wanted and wanted in norm(h.get_text(" ", strip=True)):
                heading = h
                break
        if not heading:
            continue
        links = []
        node = heading.find_next_sibling()
        while node is not None and node.name not in {"h2", "h3", "h4", "h5"}:
            for a in node.find_all("a", href=True) if hasattr(node, "find_all") else []:
                links.append((clean(a.get_text(" ", strip=True)), urljoin(SUNWATER_EAP_INDEX, a["href"])))
            node = node.find_next_sibling()
        eap = next((u for t, u in links if "emergency action plan" in t.lower() or u.lower().endswith(".pdf")), None)
        output[source["dam_id"]] = {"eap_url": eap, "emergency_info_url": SUNWATER_EAP_INDEX}
    return output


def fetch_pdf(session: requests.Session, urls: list[str]) -> tuple[bytes, str]:
    errors = []
    for url in dict.fromkeys(u for u in urls if u):
        try:
            response = session.get(url, timeout=180, allow_redirects=True,
                                   headers={"Referer": DIRECTORY_URL, "Accept": "application/pdf,*/*;q=0.8"})
            response.raise_for_status()
            content_type = response.headers.get("content-type", "").lower()
            if not response.content.startswith(b"%PDF") and "pdf" not in content_type:
                raise RuntimeError(f"response was not a PDF ({content_type or 'unknown content type'})")
            if len(response.content) > 80 * 1024 * 1024:
                raise RuntimeError("PDF exceeds the 80 MB audit limit")
            return response.content, response.url
        except Exception as exc:
            errors.append(f"{url}: {exc}")
    raise RuntimeError("; ".join(errors) if errors else "no PDF URL was available")


def extract_pdf_text(content: bytes) -> tuple[list[str], int]:
    reader = PdfReader(io.BytesIO(content), strict=False)
    page_count = len(reader.pages)
    texts: list[str] = []
    # Quick-reference and document-control information is normally near the front.
    for idx, page in enumerate(reader.pages):
        if idx >= 30:
            break
        try:
            text = page.extract_text() or ""
        except Exception as exc:
            LOG.warning("PDF page %s extraction failed: %s", idx + 1, exc)
            text = ""
        lower = text.lower()
        if idx < 12 or "activation quick reference" in lower or "flood operations" in lower or "document control" in lower:
            texts.append(f"\n--- PAGE {idx + 1} ---\n{text}")
    return texts, page_count


def parse_date(text: str | None) -> str | None:
    if not text:
        return None
    try:
        dt = date_parser.parse(clean(text), dayfirst=True, fuzzy=True)
        return dt.date().isoformat()
    except Exception:
        return None


def parse_metadata(text: str) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    patterns = [
        ("version", r"(?:ISSUE|Version|EAP\s+Version)\s*[:\-]?\s*([0-9]+(?:\.[0-9]+){0,2})"),
        ("expiry_date", r"(?:Expiry|Approved[^\n]{0,40}?until|expires?)\s*[:\-]?\s*(\d{1,2}\s+[A-Za-z]+\s+20\d{2})"),
        ("approved_date", r"(?:Approval date|Approved on|Date approved)\s*[:\-]?\s*(\d{1,2}\s+[A-Za-z]+\s+20\d{2})"),
    ]
    for key, pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            metadata[key] = parse_date(match.group(1)) if key.endswith("_date") else clean(match.group(1))
    fsl_patterns = [
        r"(?:Full Supply Level|FSL)\s*(?:\([^)]*\))?\s*[:=]?\s*(\d{1,3}(?:\.\d+)?)\s*m\s*AHD",
        r"FSL\s*(\d{1,3}(?:\.\d+)?)\s*m",
    ]
    for pattern in fsl_patterns:
        match = re.search(pattern, text, re.I)
        if match:
            metadata["fsl_m_ahd"] = float(match.group(1))
            break
    return metadata


def numeric_condition(metric: str, op: str, value: float, label: str, unit: str = "m AHD") -> dict[str, Any]:
    return {"metric": metric, "op": op, "value": value, "label": label, "unit": unit,
            "publicly_observable": True, "machine_extracted": True}


def machine_extract_rules(text: str) -> list[dict[str, Any]]:
    """Conservative patterns for the flood-operation quick-reference row.

    Ambiguous levels are retained in the document excerpt but not converted into
    assessable rules. This avoids mixing structural/earthquake hazards with flood
    operations merely because they contain elevations.
    """
    compact = clean(text)
    rules: list[dict[str, Any]] = []

    # Sunwater-style quick-reference wording.
    alert = re.search(r"(?:Flood operations.{0,900}?)EL\s*(\d{2,3}(?:\.\d+)?)\s*m?\s*(?:AHD)?\s*and\s*rising", compact, re.I)
    lean = re.search(r"Storage\s+above\s+FSL\s*(\d{2,3}(?:\.\d+)?)\s*m?", compact, re.I)
    stand = re.search(r"Storage\s+above\s+EL\s*(\d{2,3}(?:\.\d+)?)\s*m?", compact, re.I)
    if alert:
        value = float(alert.group(1))
        rules.append({"level": "alert", "hazard": "flood_operations",
                      "text": f"Machine-extracted: elevation {value:.2f} m AHD and rising.",
                      "conditions": [numeric_condition("storage_level_m", ">=", value, f"Storage level is at or above {value:.2f} m AHD"),
                                     {"metric": "storage_level_trend", "op": "==", "value": "rising", "label": "Storage level is rising", "publicly_observable": True, "machine_extracted": True}],
                      "source_page": "Machine-extracted quick reference"})
    if lean:
        value = float(lean.group(1))
        rules.append({"level": "lean_forward", "hazard": "flood_operations",
                      "text": f"Machine-extracted: storage above FSL {value:.2f} m AHD.",
                      "conditions": [numeric_condition("storage_level_m", ">", value, f"Storage level is above FSL {value:.2f} m AHD")],
                      "source_page": "Machine-extracted quick reference"})
    if stand:
        value = float(stand.group(1))
        rules.append({"level": "stand_up", "hazard": "flood_operations",
                      "text": f"Machine-extracted: storage above elevation {value:.2f} m AHD.",
                      "conditions": [numeric_condition("storage_level_m", ">", value, f"Storage level is above {value:.2f} m AHD")],
                      "source_page": "Machine-extracted quick reference"})

    # Seqwater-style standardised thresholds. Require explicit labels so other
    # elevations in the PDF are not misclassified.
    fsl = re.search(r"(?:at|above|reaches?).{0,80}?FSL\s*(\d{1,3}(?:\.\d+)?)\s*m\s*AHD", compact, re.I)
    flood_record = re.search(r"Flood\s+of\s+Record.{0,100}?(\d{1,3}(?:\.\d+)?)\s*m\s*AHD", compact, re.I)
    extreme = re.search(r"Extreme\s+Flood\s+Level.{0,100}?(\d{1,3}(?:\.\d+)?)\s*m\s*AHD", compact, re.I)
    if fsl and not any(x["level"] == "alert" for x in rules):
        value = float(fsl.group(1))
        conditions = [numeric_condition("storage_level_m", ">=", value, f"Lake level is at or above FSL {value:.2f} m AHD")]
        if re.search(r"Bureau.{0,120}?(?:flood warning|warning)", compact, re.I):
            conditions.append({"metric": "bom_flood_warning_expected", "op": "==", "value": True,
                               "label": "A relevant Bureau flood warning is expected", "publicly_observable": False,
                               "machine_extracted": True})
        rules.append({"level": "alert", "hazard": "flood_operations",
                      "text": f"Machine-extracted FSL alert threshold: {value:.2f} m AHD; consult the EAP for additional conditions.",
                      "conditions": conditions, "source_page": "Machine-extracted quick reference"})
    if flood_record and not any(x["level"] == "lean_forward" for x in rules):
        value = float(flood_record.group(1))
        rules.append({"level": "lean_forward", "hazard": "flood_operations",
                      "text": f"Machine-extracted Flood of Record threshold: {value:.2f} m AHD; forecast/model conditions may also apply.",
                      "conditions": [numeric_condition("storage_level_m", ">=", value, f"Lake level is at or above Flood of Record {value:.2f} m AHD")],
                      "source_page": "Machine-extracted quick reference"})
    if extreme and not any(x["level"] == "stand_up" for x in rules):
        value = float(extreme.group(1))
        rules.append({"level": "stand_up", "hazard": "flood_operations",
                      "text": f"Machine-extracted Extreme Flood Level threshold: {value:.2f} m AHD; engineering and evacuation assessments may also apply.",
                      "conditions": [numeric_condition("storage_level_m", ">=", value, f"Lake level is at or above Extreme Flood Level {value:.2f} m AHD")],
                      "source_page": "Machine-extracted quick reference"})
    return rules


def excerpt(text: str, max_chars: int = 9000) -> str:
    lower = text.lower()
    starts = [p for p in (lower.find("emergency activation quick reference"), lower.find("flood operations")) if p >= 0]
    start = min(starts) if starts else 0
    return clean(text[start:start + max_chars])


def build_seed_record(source: dict[str, Any], override: dict[str, Any] | None, prior: dict[str, Any] | None) -> dict[str, Any]:
    record = copy.deepcopy(prior or {})
    record.update({
        "dam_id": source["dam_id"],
        "referable": bool(source.get("referable", True)),
        "directory_name": source.get("directory_name"),
        "operator": source.get("operator"),
        "directory_url": source.get("directory_url") or DIRECTORY_URL,
        "checked_at": now_iso(),
    })
    if not source.get("referable", True):
        record.update({"document_status": "not_listed", "review_status": "not_applicable", "rules": [],
                       "notes": source.get("notes") or "No public referable-dam EAP located."})
    elif override:
        record.update(copy.deepcopy(override))
        record["document_status"] = "available"
    else:
        record.setdefault("document_status", "pending_audit")
        record.setdefault("review_status", "pending")
        record.setdefault("rules", [])
    return record


def run(force: bool = False, dam_filter: set[str] | None = None) -> int:
    started = now_iso()
    sources = read_json(CONFIG / "eap_sources.json", [])
    overrides = read_json(CONFIG / "eap_overrides.json", {})
    previous_payload = read_json(DATA / "eap_documents.json", {"dams": {}})
    previous = previous_payload.get("dams", {})
    if not sources:
        raise RuntimeError("config/eap_sources.json is missing or empty")

    session = make_session()
    directory_links: dict[str, dict[str, str]] = {}
    sunwater_links: dict[str, dict[str, str]] = {}
    discovery_errors: list[str] = []
    try:
        directory_links = discover_directory_links(session, sources)
    except Exception as exc:
        LOG.exception("Official EAP directory discovery failed")
        discovery_errors.append(f"directory: {exc}")
    try:
        sunwater_links = discover_sunwater_links(session, sources)
    except Exception as exc:
        LOG.warning("Sunwater EAP link discovery failed: %s", exc)
        discovery_errors.append(f"Sunwater index: {exc}")

    result: dict[str, dict[str, Any]] = {}
    counts = {"manually_verified": 0, "machine_extracted": 0, "document_only": 0,
              "pending_audit": 0, "not_listed": 0, "failed": 0, "change_detected": 0}

    for source in sources:
        dam_id = source["dam_id"]
        override = overrides.get(dam_id)
        prior = previous.get(dam_id)
        record = build_seed_record(source, override, prior)
        discovered = directory_links.get(dam_id, {})
        operator_discovered = sunwater_links.get(dam_id, {})
        record["emergency_info_url"] = discovered.get("emergency_info_url") or operator_discovered.get("emergency_info_url") or record.get("emergency_info_url")
        candidate_urls = [operator_discovered.get("eap_url"), discovered.get("eap_url"),
                          override.get("eap_url") if override else None, record.get("eap_url")]
        candidate_urls = [x for x in candidate_urls if x]
        if candidate_urls:
            record["discovered_eap_url"] = candidate_urls[0]
            record["eap_url"] = candidate_urls[0]
        if not record.get("referable"):
            result[dam_id] = record
            counts["not_listed"] += 1
            continue
        if dam_filter and dam_id not in dam_filter:
            result[dam_id] = record
            counts[record.get("review_status", "pending_audit") if record.get("review_status") in counts else "pending_audit"] += 1
            continue

        # Audit every run of the weekly workflow. The hash and changed flag make
        # document replacement visible rather than silently trusting old rules.
        try:
            pdf, final_url = fetch_pdf(session, candidate_urls)
            digest = hashlib.sha256(pdf).hexdigest()
            texts, page_count = extract_pdf_text(pdf)
            joined = "\n".join(texts)
            metadata = parse_metadata(joined)
            extracted_rules = machine_extract_rules(joined)
            old_hash = prior.get("sha256") if prior else None
            changed = bool(old_hash and old_hash != digest)
            record.update({
                "eap_url": final_url,
                "sha256": digest,
                "page_count": page_count,
                "downloaded_at": started,
                "fetch_error": None,
                "quick_reference_excerpt": excerpt(joined),
                **{k: v for k, v in metadata.items() if v is not None},
            })
            if override:
                # Manually verified rules remain in force only while the audited
                # document hash is unchanged or has not previously been recorded.
                record.update({k: copy.deepcopy(v) for k, v in override.items() if k in {"rules", "notes", "stand_down_text", "fsl_m_ahd"}})
                record["review_status"] = "change_detected" if changed else "manually_verified"
                record["document_status"] = "available"
            elif extracted_rules:
                record["rules"] = extracted_rules
                record["review_status"] = "machine_extracted"
                record["document_status"] = "available"
            else:
                record["rules"] = []
                record["review_status"] = "document_only"
                record["document_status"] = "available"
            record["document_changed"] = changed
        except Exception as exc:
            LOG.warning("%s EAP audit failed: %s", dam_id, exc)
            record["fetch_error"] = str(exc)
            record["checked_at"] = started
            if prior and prior.get("document_status") == "available":
                record["document_status"] = "available_cached"
                record["retained_previous"] = True
            elif override:
                record["document_status"] = "link_unavailable_rules_cached"
            else:
                record["document_status"] = "pending_audit"
                record["review_status"] = "pending"

        status_key = record.get("review_status")
        if status_key not in counts:
            status_key = "pending_audit" if record.get("document_status", "").startswith("pending") else "failed"
        counts[status_key] += 1
        result[dam_id] = record

    payload = {
        "generated_at": started,
        "directory_url": DIRECTORY_URL,
        "sunwater_eap_index": SUNWATER_EAP_INDEX,
        "discovery_errors": discovery_errors,
        "counts": counts,
        "disclaimer": "Flood-trigger rules are an informational interpretation of published EAP material. They do not report or determine formal EAP activation.",
        "dams": result,
    }
    write_json(DATA / "eap_documents.json", payload)
    LOG.info("EAP audit completed: %s", counts)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Reserved for future conditional-download support")
    parser.add_argument("--dam", action="append", default=[], help="Audit one dam id; may be repeated")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    try:
        return run(args.force, set(args.dam) if args.dam else None)
    except Exception:
        LOG.exception("EAP audit terminated")
        return 2


if __name__ == "__main__":
    sys.exit(main())
