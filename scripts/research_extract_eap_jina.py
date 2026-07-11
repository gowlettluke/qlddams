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
    return "\n".join(selected[:2500])


def reader_url(source_url: str) -> str:
    parsed = urlparse(source_url)
    # Jina's public reader supports the original scheme nested after its host.
    return f"https://r.jina.ai/http://{parsed.netloc}{parsed.path}"


def main() -> None:
    manifest: dict[str, dict] = {}
    session = requests.Session()
    for source in SOURCES:
        dam_id = source["dam_id"]
        url = source.get("eap_url")
        rec = {"dam_id": dam_id, "source_url": url, "status": "not_applicable" if not url else "failed"}
        if not url:
            manifest[dam_id] = rec
            continue
        jina = reader_url(url)
        rec["reader_url"] = jina
        try:
            response = session.get(
                jina,
                timeout=300,
                allow_redirects=True,
                impersonate="chrome",
                headers={"Accept": "text/plain,text/markdown,*/*", "X-Return-Format": "markdown"},
            )
            text = response.text
            rec.update({
                "http_status": response.status_code,
                "bytes": len(response.content),
                "content_type": response.headers.get("content-type"),
                "prefix": text[:300],
            })
            if response.status_code < 400 and len(text) > 500 and "just a moment" not in text.lower():
                (OUT / f"{dam_id}.txt").write_text(text, encoding="utf-8")
                (OUT / f"{dam_id}.focus.txt").write_text(focus(text), encoding="utf-8")
                rec["status"] = "ok"
        except Exception as exc:
            rec["error"] = repr(exc)
        manifest[dam_id] = rec
        (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print(dam_id, rec["status"], flush=True)
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
