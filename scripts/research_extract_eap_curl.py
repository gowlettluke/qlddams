from __future__ import annotations

import hashlib
import json
import re
import tempfile
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from curl_cffi import requests
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research_eap_curl"
OUT.mkdir(exist_ok=True)
INDEX = "https://www.business.qld.gov.au/industries/mining-energy-water/water/industry-infrastructure/dams/referable-dam-eaps"

DAMS = {
    "atkinson-dam": "Atkinson Dam", "baroon-pocket-dam": "Baroon Pocket Dam",
    "bill-gunn-dam": "Bill Gunn Dam", "bjelke-petersen-dam": "Bjelke-Petersen Dam",
    "boondooma-dam": "Boondooma Dam", "borumba-dam": "Borumba Dam",
    "burdekin-falls-dam": "Burdekin Falls Dam", "callide-dam": "Callide Dam",
    "cania-dam": "Cania Dam", "cedar-pocket-dam": "Cedar Pocket Dam",
    "clarendon-dam": "Clarendon Dam", "coolmunda-dam": "Coolmunda Dam",
    "cooloolabin-dam": "Cooloolabin Dam", "e-j-beardmore-dam": "EJ Beardmore Dam",
    "enoggera-dam": "Enoggera Dam", "eungella-dam": "Eungella Dam",
    "ewen-maddock-dam": "Ewen Maddock Dam", "fairbairn-dam": "Fairbairn Dam",
    "fred-haigh-dam": "Fred Haigh Dam", "glenlyon-dam": "Glenlyon Dam",
    "gold-creek-dam": "Gold Creek Dam", "hinze-dam": "Hinze Dam",
    "julius-dam": "Julius Dam", "kinchant-dam": "Kinchant Dam",
    "kroombit-dam": "Kroombit Dam", "lake-macdonald-dam": "Lake MacDonald Dam",
    "lake-manchester-dam": "Lake Manchester Dam", "leslie-dam": "Leslie Dam",
    "leslie-harrison-dam": "Leslie Harrison Dam", "little-nerang-dam": "Little Nerang Dam",
    "maroon-dam": "Maroon Dam", "moogerah-dam": "Moogerah Dam",
    "north-pine-dam": "North Pine Dam", "paradise-dam": "Paradise Dam",
    "peter-faust-dam": "Peter Faust Dam", "poona-dam": "Poona Dam",
    "sideling-creek-dam": "Sideling Creek Dam", "somerset-dam": "Somerset Dam",
    "teemburra-dam": "Teemburra Dam", "tinaroo-falls-dam": "Tinaroo Falls Dam",
    "wappa-dam": "Wappa Dam", "wivenhoe-dam": "Wivenhoe Dam",
    "wuruma-dam": "Wuruma Dam", "wyaralong-dam": "Wyaralong Dam",
}

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


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def focus(text: str) -> str:
    lines = [re.sub(r"\s+", " ", x).strip() for x in text.splitlines()]
    keys = ("quick reference", "flood event", "flood operation", "alert", "lean forward", "stand up", "stand down", "full supply", "flood of record", "extreme flood", "dam crest", "storage level", "lake level", "reservoir level", "spillway", "warning", "predicted", "modelling")
    selected: list[str] = []
    seen: set[str] = set()
    for i, line in enumerate(lines):
        if line and any(k in line.lower() for k in keys):
            for nearby in lines[max(0, i - 3): min(len(lines), i + 8)]:
                if nearby and nearby not in seen:
                    seen.add(nearby)
                    selected.append(nearby)
    return "\n".join(selected[:1500])


def fetch(session, url: str, referer: str | None = None):
    headers = {"Accept": "application/pdf,text/html;q=0.9,*/*;q=0.8", "Accept-Language": "en-AU,en;q=0.9"}
    if referer:
        headers["Referer"] = referer
    return session.get(url, headers=headers, timeout=180, allow_redirects=True, impersonate="chrome")


def main() -> None:
    session = requests.Session()
    index_response = fetch(session, INDEX)
    index_response.raise_for_status()
    soup = BeautifulSoup(index_response.text, "html.parser")
    links: list[tuple[str, str]] = []
    for a in soup.find_all("a", href=True):
        text = a.get_text(" ", strip=True)
        href = urljoin(INDEX, a["href"])
        if "eap" in text.lower() and ".pdf" in href.lower():
            links.append((text, href))

    manifest: dict[str, dict] = {}
    for dam_id, dam_name in DAMS.items():
        candidates = [u for t, u in links if norm(dam_name) in norm(t)]
        if dam_id in SUNWATER_FALLBACKS:
            candidates.append(SUNWATER_FALLBACKS[dam_id])
        candidates = list(dict.fromkeys(candidates))
        rec: dict = {"dam_id": dam_id, "dam_name": dam_name, "candidate_urls": candidates, "attempts": [], "status": "not_found"}
        for url in candidates:
            try:
                response = fetch(session, url, INDEX)
                body = response.content
                attempt = {"url": url, "status": response.status_code, "content_type": response.headers.get("content-type"), "bytes": len(body), "final_url": str(response.url), "prefix": body[:80].decode("utf-8", "replace")}
                rec["attempts"].append(attempt)
                if response.status_code >= 400 or not body.lstrip().startswith(b"%PDF"):
                    continue
                sha = hashlib.sha256(body).hexdigest()
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                    tmp.write(body)
                    path = Path(tmp.name)
                reader = PdfReader(str(path))
                page_texts = []
                for page_no, page in enumerate(reader.pages, start=1):
                    try:
                        page_texts.append(f"\n===== PDF PAGE {page_no} =====\n" + (page.extract_text() or ""))
                    except Exception as exc:
                        page_texts.append(f"\n===== PDF PAGE {page_no} =====\n[extract error: {exc}]")
                path.unlink(missing_ok=True)
                text = "\n".join(page_texts)
                (OUT / f"{dam_id}.txt").write_text(text, encoding="utf-8")
                (OUT / f"{dam_id}.focus.txt").write_text(focus(text), encoding="utf-8")
                rec.update({"status": "ok", "source_url": url, "sha256": sha, "pages": len(reader.pages)})
                break
            except Exception as exc:
                rec["attempts"].append({"url": url, "error": repr(exc)})
        manifest[dam_id] = rec
        (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print(dam_id, rec["status"], flush=True)

    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
