from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse

from curl_cffi import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research_eap_jina"
OUT.mkdir(exist_ok=True)
SOURCES = json.loads((ROOT / "config/eap_sources.json").read_text(encoding="utf-8"))
DOCUMENTS_PATH = ROOT / "data/eap_documents.json"
DOCUMENTS = json.loads(DOCUMENTS_PATH.read_text(encoding="utf-8")) if DOCUMENTS_PATH.exists() else {"dams": {}}

SUNWATER_FALLBACKS = {
    "callide-dam": "https://www.sunwater.com.au/wp-content/uploads/Home/Community/Preparing-for-weather-events/Emergency-Management/EAPs/Callide_Dam_EAP_2026.pdf",
    "e-j-beardmore-dam": "https://www.sunwater.com.au/wp-content/uploads/Home/Community/Preparing-for-weather-events/Emergency-Management/EAPs/EJ_Beardmore_Dam_EAP.pdf",
    "eungella-dam": "https://www.sunwater.com.au/wp-content/uploads/Home/Community/Preparing-for-weather-events/Emergency-Management/EAPs/Eungella_Dam_EAP_i9.0.pdf",
    "fred-haigh-dam": "https://www.sunwater.com.au/wp-content/uploads/Home/Community/Preparing-for-weather-events/Emergency-Management/EAPs/Fred_Haigh_Dam_EAP.pdf",
    "kinchant-dam": "https://www.sunwater.com.au/wp-content/uploads/Home/Community/Preparing-for-weather-events/Emergency-Management/EAPs/Kinchant_Dam_EAP.pdf",
    "peter-faust-dam": "https://www.sunwater.com.au/wp-content/uploads/Home/Community/Preparing-for-weather-events/Emergency-Management/EAPs/Peter_Faust_Dam_EAP.pdf",
    "tinaroo-falls-dam": "https://www.sunwater.com.au/wp-content/uploads/Home/Community/Preparing-for-weather-events/Emergency-Management/EAPs/Tinaroo_Falls_Dam_EAP.pdf",
    "wuruma-dam": "https://www.sunwater.com.au/wp-content/uploads/Home/Community/Preparing-for-weather-events/Emergency-Management/EAPs/Wuruma_Dam_EAP.pdf",
}


def focus(text: str) -> str:
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    keys = (
        "quick reference", "flood event", "flood operation", "alert", "lean forward",
        "stand up", "stand down", "full supply", "flood of record", "extreme flood",
        "dam crest", "storage level", "lake level", "reservoir level", "spillway",
        "bureau", "warning", "predicted", "modelling", "activation level",
    )
    selected: list[str] = []
    seen: set[str] = set()
    for i, line in enumerate(lines):
        if line and any(key in line.lower() for key in keys):
            for value in lines[max(0, i - 4): min(len(lines), i + 10)]:
                if value and value not in seen:
                    seen.add(value)
                    selected.append(value)
    return "\n".join(selected[:3000])


def reader_urls(source_url: str) -> list[str]:
    parsed = urlparse(source_url)
    # Try both schemes. The public reader may be able to retrieve the original
    # public PDF even when the government CDN challenges an automated client.
    return [
        f"https://r.jina.ai/http://{parsed.netloc}{parsed.path}",
        f"https://r.jina.ai/https://{parsed.netloc}{parsed.path}",
    ]


def main() -> None:
    manifest: dict[str, dict] = {}
    session = requests.Session()
    document_map = DOCUMENTS.get("dams", {}) if isinstance(DOCUMENTS, dict) else {}

    for source in SOURCES:
        dam_id = source["dam_id"]
        candidates: list[str] = []
        existing = document_map.get(dam_id, {}) if isinstance(document_map, dict) else {}
        for key in ("eap_url", "discovered_eap_url", "document_url"):
            value = existing.get(key) if isinstance(existing, dict) else None
            if value:
                candidates.append(value)
        if dam_id in SUNWATER_FALLBACKS:
            candidates.append(SUNWATER_FALLBACKS[dam_id])
        candidates = list(dict.fromkeys(candidates))

        rec: dict = {
            "dam_id": dam_id,
            "candidate_urls": candidates,
            "attempts": [],
            "status": "not_applicable" if not candidates else "failed",
        }
        for source_url in candidates:
            for jina in reader_urls(source_url):
                attempt = {"source_url": source_url, "reader_url": jina}
                try:
                    response = session.get(
                        jina,
                        timeout=180,
                        allow_redirects=True,
                        impersonate="chrome",
                        headers={"Accept": "text/plain,text/markdown,*/*", "X-Return-Format": "markdown"},
                    )
                    text = response.text
                    attempt.update({
                        "http_status": response.status_code,
                        "bytes": len(response.content),
                        "content_type": response.headers.get("content-type"),
                        "prefix": text[:300],
                    })
                    rec["attempts"].append(attempt)
                    if response.status_code < 400 and len(text) > 500 and "just a moment" not in text.lower():
                        (OUT / f"{dam_id}.txt").write_text(text, encoding="utf-8")
                        (OUT / f"{dam_id}.focus.txt").write_text(focus(text), encoding="utf-8")
                        rec.update({"status": "ok", "source_url": source_url, "reader_url": jina, "bytes": len(response.content)})
                        break
                except Exception as exc:
                    attempt["error"] = repr(exc)
                    rec["attempts"].append(attempt)
            if rec["status"] == "ok":
                break
        manifest[dam_id] = rec
        (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print(dam_id, rec["status"], flush=True)
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
