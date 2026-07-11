from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research_eap_extract"
OUT.mkdir(exist_ok=True)
INDEX = "https://www.business.qld.gov.au/industries/mining-energy-water/water/industry-infrastructure/dams/referable-dam-eaps"

DAMS = {
    "atkinson-dam": "Atkinson Dam",
    "baroon-pocket-dam": "Baroon Pocket Dam",
    "bill-gunn-dam": "Bill Gunn Dam",
    "bjelke-petersen-dam": "Bjelke-Petersen Dam",
    "boondooma-dam": "Boondooma Dam",
    "borumba-dam": "Borumba Dam",
    "burdekin-falls-dam": "Burdekin Falls Dam",
    "callide-dam": "Callide Dam",
    "cania-dam": "Cania Dam",
    "cedar-pocket-dam": "Cedar Pocket Dam",
    "clarendon-dam": "Clarendon Dam",
    "coolmunda-dam": "Coolmunda Dam",
    "cooloolabin-dam": "Cooloolabin Dam",
    "e-j-beardmore-dam": "EJ Beardmore Dam",
    "enoggera-dam": "Enoggera Dam",
    "eungella-dam": "Eungella Dam",
    "ewen-maddock-dam": "Ewen Maddock Dam",
    "fairbairn-dam": "Fairbairn Dam",
    "fred-haigh-dam": "Fred Haigh Dam",
    "glenlyon-dam": "Glenlyon Dam",
    "gold-creek-dam": "Gold Creek Dam",
    "hinze-dam": "Hinze Dam",
    "julius-dam": "Julius Dam",
    "kinchant-dam": "Kinchant Dam",
    "kroombit-dam": "Kroombit Dam",
    "lake-macdonald-dam": "Lake MacDonald Dam",
    "lake-manchester-dam": "Lake Manchester Dam",
    "leslie-dam": "Leslie Dam",
    "leslie-harrison-dam": "Leslie Harrison Dam",
    "little-nerang-dam": "Little Nerang Dam",
    "maroon-dam": "Maroon Dam",
    "moogerah-dam": "Moogerah Dam",
    "north-pine-dam": "North Pine Dam",
    "paradise-dam": "Paradise Dam",
    "peter-faust-dam": "Peter Faust Dam",
    "poona-dam": "Poona Dam",
    "sideling-creek-dam": "Sideling Creek Dam",
    "somerset-dam": "Somerset Dam",
    "teemburra-dam": "Teemburra Dam",
    "tinaroo-falls-dam": "Tinaroo Falls Dam",
    "wappa-dam": "Wappa Dam",
    "wivenhoe-dam": "Wivenhoe Dam",
    "wuruma-dam": "Wuruma Dam",
    "wyaralong-dam": "Wyaralong Dam",
}


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def extract_focus(text: str) -> str:
    lines = [re.sub(r"\s+", " ", x).strip() for x in text.splitlines()]
    lines = [x for x in lines if x]
    keys = (
        "quick reference", "flood event", "alert", "lean forward", "stand up", "stand down",
        "full supply level", "flood of record", "extreme flood level", "dam crest", "storage level",
        "lake level", "reservoir level", "elevation", "spillway", "bureau", "warning", "predicted",
    )
    picked = []
    for i, line in enumerate(lines):
        if any(k in line.lower() for k in keys):
            picked.extend(lines[max(0, i-2): min(len(lines), i+4)])
    dedup=[]
    seen=set()
    for x in picked:
        if x not in seen:
            seen.add(x); dedup.append(x)
    return "\n".join(dedup[:500])


def main() -> None:
    results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/149 Safari/537.36")
        page = ctx.new_page()
        page.goto(INDEX, wait_until="networkidle", timeout=120000)
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        links=[]
        for a in soup.find_all("a", href=True):
            txt=a.get_text(" ", strip=True)
            if "EAP" in txt and ".pdf" in a["href"].lower():
                links.append((txt, urljoin(INDEX, a["href"])))
        for dam_id, dam_name in DAMS.items():
            candidates=[(t,u) for t,u in links if norm(dam_name) in norm(t)]
            rec={"dam_id":dam_id,"dam_name":dam_name,"candidates":candidates,"status":"not_found"}
            if not candidates:
                results[dam_id]=rec; continue
            url=candidates[0][1]
            rec["url"]=url
            try:
                response=ctx.request.get(url, timeout=120000, headers={"Referer":INDEX,"Accept":"application/pdf,*/*"})
                rec["http_status"]=response.status
                body=response.body()
                rec["bytes"]=len(body)
                if not body.startswith(b"%PDF"):
                    rec["status"]="not_pdf"
                    rec["body_prefix"]=body[:200].decode("utf-8","replace")
                    results[dam_id]=rec; continue
                pdf=OUT/f"{dam_id}.pdf"
                pdf.write_bytes(body)
                reader=PdfReader(str(pdf))
                pages=[]
                for page_no, pg in enumerate(reader.pages[:25]):
                    try: pages.append(pg.extract_text() or "")
                    except Exception as e: pages.append(f"[page {page_no} extraction error: {e}]")
                text="\n".join(pages)
                (OUT/f"{dam_id}.txt").write_text(text, encoding="utf-8")
                (OUT/f"{dam_id}.focus.txt").write_text(extract_focus(text), encoding="utf-8")
                rec["status"]="ok"
                rec["pages"]=len(reader.pages)
            except Exception as e:
                rec["status"]="error"; rec["error"]=repr(e)
            results[dam_id]=rec
        browser.close()
    (OUT/"manifest.json").write_text(json.dumps(results,indent=2),encoding="utf-8")
    print(json.dumps({k:v["status"] for k,v in results.items()},indent=2))

if __name__ == "__main__":
    main()
