from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse

from curl_cffi import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research_eap_jina_parallel"
OUT.mkdir(exist_ok=True)
SOURCES = json.loads((ROOT / "config/eap_sources.json").read_text(encoding="utf-8"))
DOCUMENTS = json.loads((ROOT / "data/eap_documents.json").read_text(encoding="utf-8"))

SUNWATER = {
    "callide-dam": "https://www.sunwater.com.au/wp-content/uploads/Home/Community/Preparing-for-weather-events/Emergency-Management/EAPs/Callide_Dam_EAP_2026.pdf",
    "e-j-beardmore-dam": "https://www.sunwater.com.au/wp-content/uploads/Home/Community/Preparing-for-weather-events/Emergency-Management/EAPs/EJ_Beardmore_Dam_EAP.pdf",
    "eungella-dam": "https://www.sunwater.com.au/wp-content/uploads/Home/Community/Preparing-for-weather-events/Emergency-Management/EAPs/Eungella_Dam_EAP_i9.0.pdf",
    "fred-haigh-dam": "https://www.sunwater.com.au/wp-content/uploads/Home/Community/Preparing-for-weather-events/Emergency-Management/EAPs/Fred_Haigh_Dam_EAP.pdf",
    "kinchant-dam": "https://www.sunwater.com.au/wp-content/uploads/Home/Community/Preparing-for-weather-events/Emergency-Management/EAPs/Kinchant_Dam_EAP.pdf",
    "peter-faust-dam": "https://www.sunwater.com.au/wp-content/uploads/Home/Community/Preparing-for-weather-events/Emergency-Management/EAPs/Peter_Faust_Dam_EAP.pdf",
    "tinaroo-falls-dam": "https://www.sunwater.com.au/wp-content/uploads/Home/Community/Preparing-for-weather-events/Emergency-Management/EAPs/Tinaroo_Falls_Dam_EAP.pdf",
    "wuruma-dam": "https://www.sunwater.com.au/wp-content/uploads/Home/Community/Preparing-for-weather-events/Emergency-Management/EAPs/Wuruma_Dam_EAP.pdf",
}

KEYS = (
    "quick reference", "flood event", "flood operation", "alert", "lean forward",
    "stand up", "stand down", "full supply", "flood of record", "extreme flood",
    "dam crest", "storage level", "lake level", "reservoir level", "spillway",
    "bureau", "warning", "predicted", "modelling", "activation level",
)


def focus(text: str) -> str:
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    selected, seen = [], set()
    for i, line in enumerate(lines):
        if line and any(key in line.lower() for key in KEYS):
            for value in lines[max(0, i - 5): min(len(lines), i + 12)]:
                if value and value not in seen:
                    seen.add(value); selected.append(value)
    return "\n".join(selected[:4000])


def reader_candidates(source_url: str) -> list[str]:
    p = urlparse(source_url)
    return [
        f"https://r.jina.ai/http://{p.netloc}{p.path}",
        f"https://r.jina.ai/https://{p.netloc}{p.path}",
    ]


def source_candidates(dam_id: str) -> list[str]:
    rec = DOCUMENTS.get("dams", {}).get(dam_id, {})
    urls = [rec.get("eap_url"), rec.get("discovered_eap_url"), SUNWATER.get(dam_id)]
    return list(dict.fromkeys(url for url in urls if url))


def process(source: dict) -> tuple[str, dict, str | None]:
    dam_id = source["dam_id"]
    urls = source_candidates(dam_id)
    rec = {"dam_id": dam_id, "candidate_urls": urls, "attempts": [], "status": "not_applicable" if not urls else "failed"}
    for source_url in urls:
        for reader_url in reader_candidates(source_url):
            attempt = {"source_url": source_url, "reader_url": reader_url}
            try:
                response = requests.get(
                    reader_url,
                    timeout=90,
                    allow_redirects=True,
                    impersonate="chrome",
                    headers={"Accept": "text/plain,text/markdown,*/*", "X-Return-Format": "markdown"},
                )
                text = response.text
                attempt.update({"status": response.status_code, "bytes": len(response.content), "content_type": response.headers.get("content-type"), "prefix": text[:250]})
                rec["attempts"].append(attempt)
                if response.status_code < 400 and len(text) > 500 and "just a moment" not in text.lower():
                    rec.update({"status": "ok", "source_url": source_url, "reader_url": reader_url, "bytes": len(response.content)})
                    return dam_id, rec, text
            except Exception as exc:
                attempt["error"] = repr(exc); rec["attempts"].append(attempt)
    return dam_id, rec, None


def main() -> None:
    manifest: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=12) as pool:
        futures = {pool.submit(process, source): source["dam_id"] for source in SOURCES}
        for future in as_completed(futures):
            dam_id, rec, text = future.result()
            manifest[dam_id] = rec
            if text:
                (OUT / f"{dam_id}.txt").write_text(text, encoding="utf-8")
                (OUT / f"{dam_id}.focus.txt").write_text(focus(text), encoding="utf-8")
            (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            print(dam_id, rec["status"], flush=True)
    ordered = {source["dam_id"]: manifest[source["dam_id"]] for source in SOURCES}
    (OUT / "manifest.json").write_text(json.dumps(ordered, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
