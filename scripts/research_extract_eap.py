from __future__ import annotations

import json
import re
import tempfile
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from playwright.sync_api import Download, Page, Response, TimeoutError as PlaywrightTimeoutError, sync_playwright
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research_eap_extract"
OUT.mkdir(exist_ok=True)
INDEX = "https://www.business.qld.gov.au/industries/mining-energy-water/water/industry-infrastructure/dams/referable-dam-eaps"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
)

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
        "quick reference",
        "flood event",
        "flood operations",
        "alert",
        "lean forward",
        "stand up",
        "stand down",
        "full supply level",
        "flood of record",
        "extreme flood level",
        "dam crest",
        "storage level",
        "lake level",
        "reservoir level",
        "elevation",
        "spillway",
        "bureau",
        "warning",
        "predicted",
    )
    picked: list[str] = []
    for i, line in enumerate(lines):
        if any(k in line.lower() for k in keys):
            picked.extend(lines[max(0, i - 3) : min(len(lines), i + 6)])
    dedup: list[str] = []
    seen: set[str] = set()
    for value in picked:
        if value not in seen:
            seen.add(value)
            dedup.append(value)
    return "\n".join(dedup[:900])


def is_pdf(body: bytes) -> bool:
    return body.lstrip().startswith(b"%PDF")


def body_from_response(response: Response | None) -> bytes | None:
    if response is None:
        return None
    try:
        body = response.body()
    except Exception:
        return None
    return body if is_pdf(body) else None


def fetch_pdf_via_browser(page: Page, url: str, referer: str) -> tuple[bytes | None, dict]:
    diagnostics: dict = {"attempts": []}
    page.set_extra_http_headers(
        {
            "Referer": referer,
            "Accept": "application/pdf,application/octet-stream;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-AU,en;q=0.9",
        }
    )

    captured: list[bytes] = []

    def on_response(response: Response) -> None:
        try:
            ctype = (response.headers.get("content-type") or "").lower()
            if "application/pdf" in ctype:
                data = response.body()
                if is_pdf(data):
                    captured.append(data)
        except Exception:
            pass

    page.on("response", on_response)

    # Attempt 1: a genuine browser navigation. This is intentionally not
    # browser_context.request.get(); Cloudflare treats those very differently.
    try:
        response = page.goto(url, wait_until="commit", timeout=120_000)
        diagnostics["attempts"].append(
            {
                "method": "page.goto",
                "status": None if response is None else response.status,
                "url": page.url,
            }
        )
        body = body_from_response(response)
        if body:
            return body, diagnostics

        # A JS challenge can redirect after the initial commit. Give it time to
        # complete, then inspect any subsequent PDF response captured above.
        for _ in range(30):
            page.wait_for_timeout(1_000)
            if captured:
                return captured[-1], diagnostics
            title = ""
            try:
                title = page.title()
            except Exception:
                pass
            if "just a moment" not in title.lower() and "challenge" not in title.lower():
                break
    except PlaywrightTimeoutError as exc:
        diagnostics["attempts"].append({"method": "page.goto", "error": repr(exc)})
    except Exception as exc:
        diagnostics["attempts"].append({"method": "page.goto", "error": repr(exc)})

    if captured:
        return captured[-1], diagnostics

    # Attempt 2: once a real browser page has run the challenge, reuse its
    # cookies in the context request client.
    try:
        response = page.context.request.get(
            url,
            timeout=120_000,
            headers={
                "Referer": referer,
                "Accept": "application/pdf,application/octet-stream;q=0.9,*/*;q=0.8",
                "User-Agent": USER_AGENT,
            },
        )
        body = response.body()
        diagnostics["attempts"].append(
            {
                "method": "context.request.after_browser",
                "status": response.status,
                "bytes": len(body),
                "content_type": response.headers.get("content-type"),
            }
        )
        if is_pdf(body):
            return body, diagnostics
    except Exception as exc:
        diagnostics["attempts"].append(
            {"method": "context.request.after_browser", "error": repr(exc)}
        )

    # Attempt 3: disable the built-in PDF viewer and trigger a normal anchor
    # click. Some servers use Content-Disposition only after navigation from the
    # directory page.
    try:
        page.goto(referer, wait_until="domcontentloaded", timeout=120_000)
        href = url
        with page.expect_download(timeout=60_000) as download_info:
            page.evaluate(
                "href => { const a=document.createElement('a'); a.href=href; a.download=''; document.body.appendChild(a); a.click(); }",
                href,
            )
        download: Download = download_info.value
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            temp_path = Path(tmp.name)
        download.save_as(str(temp_path))
        body = temp_path.read_bytes()
        temp_path.unlink(missing_ok=True)
        diagnostics["attempts"].append(
            {"method": "anchor_download", "bytes": len(body), "suggested": download.suggested_filename}
        )
        if is_pdf(body):
            return body, diagnostics
    except Exception as exc:
        diagnostics["attempts"].append({"method": "anchor_download", "error": repr(exc)})

    return None, diagnostics


def main() -> None:
    results: dict[str, dict] = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-pdf-extension",
            ],
        )
        ctx = browser.new_context(
            user_agent=USER_AGENT,
            locale="en-AU",
            timezone_id="Australia/Brisbane",
            accept_downloads=True,
            viewport={"width": 1365, "height": 900},
        )
        directory_page = ctx.new_page()
        directory_page.goto(INDEX, wait_until="networkidle", timeout=120_000)
        html = directory_page.content()
        soup = BeautifulSoup(html, "html.parser")
        links: list[tuple[str, str]] = []
        for anchor in soup.find_all("a", href=True):
            text = anchor.get_text(" ", strip=True)
            if "EAP" in text and ".pdf" in anchor["href"].lower():
                links.append((text, urljoin(INDEX, anchor["href"])))

        for dam_id, dam_name in DAMS.items():
            candidates = [(t, u) for t, u in links if norm(dam_name) in norm(t)]
            rec: dict = {
                "dam_id": dam_id,
                "dam_name": dam_name,
                "candidates": candidates,
                "status": "not_found",
            }
            if not candidates:
                results[dam_id] = rec
                continue

            url = candidates[0][1]
            rec["url"] = url
            page = ctx.new_page()
            try:
                body, diagnostics = fetch_pdf_via_browser(page, url, INDEX)
                rec["diagnostics"] = diagnostics
                rec["bytes"] = 0 if body is None else len(body)
                if not body:
                    rec["status"] = "not_pdf"
                    try:
                        rec["page_url"] = page.url
                        rec["page_title"] = page.title()
                        rec["body_prefix"] = page.content()[:500]
                    except Exception:
                        pass
                    results[dam_id] = rec
                    continue

                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                    pdf_path = Path(tmp.name)
                    pdf_path.write_bytes(body)
                reader = PdfReader(str(pdf_path))
                pages: list[str] = []
                for page_no, pdf_page in enumerate(reader.pages):
                    try:
                        extracted = pdf_page.extract_text() or ""
                    except Exception as exc:
                        extracted = f"[page {page_no + 1} extraction error: {exc}]"
                    pages.append(f"\n===== PDF PAGE {page_no + 1} =====\n{extracted}")
                pdf_path.unlink(missing_ok=True)
                text = "\n".join(pages)
                (OUT / f"{dam_id}.txt").write_text(text, encoding="utf-8")
                (OUT / f"{dam_id}.focus.txt").write_text(extract_focus(text), encoding="utf-8")
                rec["status"] = "ok"
                rec["pages"] = len(reader.pages)
            except Exception as exc:
                rec["status"] = "error"
                rec["error"] = repr(exc)
            finally:
                page.close()
            results[dam_id] = rec
            (OUT / "manifest.json").write_text(
                json.dumps(results, indent=2), encoding="utf-8"
            )

        directory_page.close()
        browser.close()

    (OUT / "manifest.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps({k: v["status"] for k, v in results.items()}, indent=2))


if __name__ == "__main__":
    main()
