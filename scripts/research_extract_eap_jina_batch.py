from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path
from urllib.parse import urlparse

from curl_cffi import requests

ROOT = Path(__file__).resolve().parents[1]

OFFICIAL_URLS = {
  "atkinson-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0010/1619632/atkinson-eap.pdf",
  "baroon-pocket-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0003/1619634/baroon-eap.pdf",
  "bill-gunn-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0006/1619637/bill-gunn-eap.pdf",
  "bjelke-petersen-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0007/1619638/bjelke-petersen-eap.pdf",
  "boondooma-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0009/1619640/boondooma-eap.pdf",
  "borumba-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0010/1619641/borumba-eap.pdf",
  "burdekin-falls-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0004/1619644/burdekin-falls-eap.pdf",
  "callide-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0011/1619660/callide-eap.pdf",
  "cania-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0004/1619671/cania-eap.pdf",
  "cedar-pocket-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0005/1619672/cedar-pocket-eap.pdf",
  "clarendon-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0008/1619675/clarendon-eap.pdf",
  "coolmunda-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0011/1619678/coolmunda-eap.pdf",
  "cooloolabin-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0012/1619679/cooloolabin-eap.pdf",
  "e-j-beardmore-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0004/1619635/beardmore-eap.pdf",
  "enoggera-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0003/1619706/enoggera-eap.pdf",
  "eungella-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0005/1619708/eungella-eap.pdf",
  "ewen-maddock-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0006/1619709/ewen-maddock-eap.pdf",
  "fairbairn-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0008/1619711/fairbairn-eap.pdf",
  "fred-haigh-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0010/1619713/fred-haigh-eap.pdf",
  "glenlyon-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0011/1619714/glenlyon-eap.pdf",
  "gold-creek-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0004/1619716/gold-creek-eap.pdf",
  "hinze-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0008/1619720/hinze-eap.pdf",
  "julius-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0004/1619725/julius-eap.pdf",
  "kinchant-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0006/1619727/kinchant-eap.pdf",
  "kroombit-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0008/1619729/kroombit-eap.pdf",
  "lake-macdonald-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0006/1619736/lake-macdonald-eap.pdf",
  "lake-manchester-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0007/1619737/lake-manchester-eap.pdf",
  "leslie-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0003/1619742/leslie-eap.pdf",
  "leslie-harrison-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0004/1619743/leslie-harrison-eap.pdf",
  "little-nerang-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0006/1619745/little-nerang-eap.pdf",
  "maroon-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0009/1619748/maroon-eap.pdf",
  "moogerah-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0006/1619754/moogerah-eap.pdf",
  "north-pine-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0010/1619758/north-pine-eap.pdf",
  "paradise-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0003/1619760/paradise-eap.pdf",
  "peter-faust-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0006/1619763/peter-faust-eap.pdf",
  "poona-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0007/1619764/poona-eap.pdf",
  "sideling-creek-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0004/1619770/sideling-creek-eap.pdf",
  "somerset-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0005/1619771/somerset-eap.pdf",
  "teemburra-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0006/1619781/teemburra-eap.pdf",
  "tinaroo-falls-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0008/1619783/tinaroo-falls-eap.pdf",
  "wappa-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0009/1619784/wappa-eap.pdf",
  "wivenhoe-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0011/1619786/wivenhoe-eap.pdf",
  "wuruma-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0004/1619788/wuruma-eap.pdf",
  "wyaralong-dam": "https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0005/1619789/wyaralong-eap.pdf"
}

KEYS = ("quick reference", "flood event", "flood operation", "alert", "lean forward", "stand up", "stand down", "full supply", "flood of record", "extreme flood", "dam crest", "storage level", "lake level", "reservoir level", "spillway", "bureau", "warning", "predicted", "modelling", "activation level")


def focus(text: str) -> str:
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    selected, seen = [], set()
    for i, line in enumerate(lines):
        if line and any(key in line.lower() for key in KEYS):
            for value in lines[max(0, i - 5): min(len(lines), i + 12)]:
                if value and value not in seen:
                    seen.add(value); selected.append(value)
    return "\n".join(selected[:5000])


def reader_urls(source_url: str) -> list[str]:
    p = urlparse(source_url)
    return [f"https://r.jina.ai/http://{p.netloc}{p.path}", f"https://r.jina.ai/https://{p.netloc}{p.path}"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=int, required=True)
    parser.add_argument("--batches", type=int, default=4)
    args = parser.parse_args()
    out = ROOT / f"research_eap_batch_{args.batch}"
    out.mkdir(exist_ok=True)
    items = [(k, v) for i, (k, v) in enumerate(OFFICIAL_URLS.items()) if i % args.batches == args.batch]
    manifest = {}
    for dam_id, source_url in items:
        rec = {"dam_id": dam_id, "source_url": source_url, "status": "failed", "attempts": []}
        for reader_url in reader_urls(source_url):
            for attempt_no in range(1, 4):
                attempt = {"reader_url": reader_url, "attempt": attempt_no}
                try:
                    response = requests.get(reader_url, timeout=120, allow_redirects=True, impersonate="chrome", headers={"Accept": "text/plain,text/markdown,*/*", "X-Return-Format": "markdown"})
                    text = response.text
                    attempt.update({"status": response.status_code, "bytes": len(response.content), "prefix": text[:250]})
                    rec["attempts"].append(attempt)
                    title_ok = dam_id.split("-dam")[0].replace("-", " ") in text.lower() or "emergency action plan" in text.lower()
                    if response.status_code < 400 and len(text) > 5000 and title_ok and "just a moment" not in text.lower():
                        (out / f"{dam_id}.txt").write_text(text, encoding="utf-8")
                        (out / f"{dam_id}.focus.txt").write_text(focus(text), encoding="utf-8")
                        rec.update({"status": "ok", "reader_url": reader_url, "bytes": len(response.content)})
                        break
                except Exception as exc:
                    attempt["error"] = repr(exc); rec["attempts"].append(attempt)
                time.sleep(2 * attempt_no)
            if rec["status"] == "ok":
                break
        manifest[dam_id] = rec
        (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print(dam_id, rec["status"], flush=True)
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
