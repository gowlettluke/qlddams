#!/usr/bin/env python3
"""Collect and normalize live Queensland dam and river-gauge data.

The dashboard is deliberately a static GitHub Pages site. This collector runs
in GitHub Actions, performs all cross-origin/source-specific work server-side,
and writes small JSON files consumed by index.html.

Design principles:
* Preserve the last good observation whenever one provider fails.
* Keep raw numeric values; formatting belongs in the browser.
* Paginate the Sunwater history API completely.
* Discover dynamic Seqwater Drupal form values instead of hard-coding tokens.
* Treat automatically selected nearby gauges as candidates, not proven
  hydrological relationships.
"""
from __future__ import annotations

import argparse
import copy
import json
import logging
import math
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config"
DATA = ROOT / "data"
HISTORY = DATA / "history"
BRISBANE = timezone(timedelta(hours=10))
USER_AGENT = "QueenslandDamDashboard/1.0 (+GitHub Pages data collector)"

SEQ_CURRENT_URL = "https://www.seqwater.com.au/dam-levels"
SEQ_HISTORY_URL = "https://www.seqwater.com.au/historic-dam-levels"
SUN_DAMS_URL = "https://www.sunwater.com.au/dams/"
SUN_HISTORY_PAGE = "https://www.sunwater.com.au/water-data/historical-dam-capacity/"
SUN_API_ROOT = "https://data.sunwater.com.au/api"
QLD_MONITORING_SITES = "https://water-monitoring.information.qld.gov.au/wgen/sites.hd.anon.xml"
BOM_RIVER_INDEX = "https://www.bom.gov.au/qld/flood/rain_river.shtml"
BOM_STATION_INDEX = "https://www.bom.gov.au/qld/flood/networks/section3.shtml"

LOG = logging.getLogger("dam-collector")

SEQ_HISTORY_FIELDS: dict[int, str] = {
    0: "Atkinson Dam", 1: "Baroon Pocket Dam", 2: "Bill Gunn Dam", 3: "Borumba Dam",
    4: "Cedar Pocket Dam", 5: "Clarendon Dam", 6: "Cooloolabin Dam", 7: "Enoggera Dam",
    8: "Ewen Maddock Dam", 9: "Gold Creek Dam", 10: "Hinze Dam", 11: "Lake Macdonald Dam",
    12: "Lake Manchester Dam", 13: "Leslie Harrison Dam", 14: "Little Nerang Dam",
    15: "Maroon Dam", 16: "Moogerah Dam", 17: "Nindooinbah Dam", 18: "North Pine Dam",
    19: "Poona Dam", 20: "Sideling Creek Dam", 21: "Somerset Dam", 22: "Wappa Dam",
    23: "Wivenhoe Dam", 24: "Wyaralong Dam",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def norm(value: Any) -> str:
    text = unicodedata.normalize("NFKD", clean_text(value)).encode("ascii", "ignore").decode().lower()
    text = text.replace("lake dyer", "bill gunn").replace("lake samsonvale", "north pine")
    text = text.replace("lake kurwongbah", "sideling creek").replace("six mile creek", "lake macdonald")
    return re.sub(r"[^a-z0-9]", "", text.replace("intake", "").replace("falls", ""))


def number(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        if isinstance(value, str):
            m = re.search(r"-?\d[\d,\s]*(?:\.\d+)?", value)
            if not m:
                return None
            value = re.sub(r"[,\s]", "", m.group(0))
        result = float(value)
        return result if math.isfinite(result) else None
    except (TypeError, ValueError):
        return None


def iso_datetime(value: Any, assume_brisbane: bool = True) -> str | None:
    if value in (None, ""):
        return None
    try:
        dt = date_parser.parse(str(value), dayfirst=True, fuzzy=False)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=BRISBANE if assume_brisbane else timezone.utc)
        return dt.isoformat(timespec="seconds")
    except Exception:
        return None


def iso_datetime_sunwater(value: Any) -> str | None:
    """Parse Sunwater timestamps without silently swapping day and month.

    Sunwater endpoints have used both ISO timestamps and slash-formatted dates.
    For an ambiguous slash date, evaluate both interpretations and choose the
    plausible instant closest to the collection time, rejecting far-future data.
    """
    if value in (None, ""):
        return None
    raw = str(value).strip()
    candidates: list[datetime] = []
    for dayfirst in (False, True):
        try:
            dt = date_parser.parse(raw, dayfirst=dayfirst, fuzzy=False)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=BRISBANE)
            candidates.append(dt)
        except Exception:
            pass
    if not candidates:
        return None
    now = datetime.now(timezone.utc)
    def score(dt: datetime) -> float:
        utc = dt.astimezone(timezone.utc)
        future_penalty = 10**10 if utc > now + timedelta(days=2) else 0
        return future_penalty + abs((utc - now).total_seconds())
    chosen = min(candidates, key=score)
    if chosen.astimezone(timezone.utc) > now + timedelta(days=2):
        return None
    return chosen.isoformat(timespec="seconds")


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


def make_session() -> requests.Session:
    retry = Retry(total=3, connect=3, read=3, backoff_factor=1.0,
                  status_forcelist=(429, 500, 502, 503, 504), allowed_methods=frozenset(("GET", "POST")))
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "en-AU,en;q=0.9"})
    adapter = HTTPAdapter(max_retries=retry, pool_connections=20, pool_maxsize=20)
    session.mount("https://", adapter)
    return session


class Registry:
    def __init__(self, dams: list[dict[str, Any]]):
        self.dams = dams
        self.by_id = {d["id"]: d for d in dams}
        self.keys: list[tuple[str, dict[str, Any]]] = []
        for dam in dams:
            for alias in list(dam.get("aliases", [])) + [dam.get("name"), dam.get("source_name")]:
                key = norm(alias)
                if key:
                    self.keys.append((key, dam))

    def match(self, name: Any, operator: str | None = None) -> dict[str, Any] | None:
        key = norm(name)
        if not key:
            return None
        exact = [d for k, d in self.keys if k == key and (not operator or d["operator"] == operator)]
        if exact:
            return exact[0]
        options: list[tuple[int, dict[str, Any]]] = []
        for candidate, dam in self.keys:
            if operator and dam["operator"] != operator:
                continue
            if len(candidate) >= 5 and (candidate in key or key in candidate):
                options.append((min(len(candidate), len(key)), dam))
        return max(options, default=(0, None), key=lambda x: x[0])[1]


def health_record(status: str, **kwargs: Any) -> dict[str, Any]:
    return {"status": status, **kwargs}


def parse_seqwater_current(session: requests.Session, registry: Registry) -> list[dict[str, Any]]:
    response = session.get(SEQ_CURRENT_URL, timeout=50)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.select(".block-seqw-dam-levels tbody tr") or soup.select("table tbody tr")
    results: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 3:
            continue
        text = clean_text(row.get_text(" ", strip=True))
        dam = registry.match(clean_text(cells[0].get_text(" ", strip=True)), "Seqwater")
        if not dam or dam["id"] in seen:
            continue
        percent = None
        for cell in cells:
            candidate = re.search(r"(-?\d+(?:\.\d+)?)\s*%", cell.get_text(" ", strip=True))
            if candidate:
                percent = float(candidate.group(1))
                break
        volumes: list[float] = []
        for cell in cells[1:]:
            if re.search(r"\bML\b", cell.get_text(" ", strip=True), re.I):
                v = number(cell.get_text(" ", strip=True))
                if v is not None:
                    volumes.append(v)
        obs_el = row.select_one(".observation")
        observed = iso_datetime(obs_el.get_text(" ", strip=True) if obs_el else None)
        if observed is None:
            for pattern in (r"Last observation\s*:?\s*([^|]+)", r"Observed\s*:?\s*([^|]+)"):
                m = re.search(pattern, text, re.I)
                if m:
                    observed = iso_datetime(m.group(1))
                    break
        info_el = row.select_one(".observation + *")
        information = clean_text(info_el.get_text(" ", strip=True)) if info_el else ""
        if information.lower() in {"", "view historical dam levels", "historical dam levels"}:
            information = ""
        results.append({
            "dam_id": dam["id"], "observed_at": observed, "percent_full": percent,
            "full_supply_volume_ml": volumes[0] if volumes else None,
            "volume_ml": volumes[1] if len(volumes) > 1 else None,
            "storage_level_m": None, "outflow_cms": None, "rainfall_mm": None, "river_level_m": None,
            "information": information or None, "source": "Seqwater", "retrieved_at": now_iso(),
            "quality_status": "live",
        })
        seen.add(dam["id"])
    if len(results) < 20:
        raise RuntimeError(f"Seqwater page parser returned only {len(results)} matched dams")
    return results


def find_nested_historical(value: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(value, dict):
        if isinstance(value.get("historical"), list):
            found.extend(x for x in value["historical"] if isinstance(x, dict))
        for child in value.values():
            found.extend(find_nested_historical(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(find_nested_historical(child))
    return found


def parse_seqwater_history(session: requests.Session, registry: Registry, days: int) -> dict[str, list[dict[str, Any]]]:
    page = session.get(SEQ_HISTORY_URL, timeout=50)
    page.raise_for_status()
    soup = BeautifulSoup(page.text, "html.parser")
    form_id_input = soup.find("input", attrs={"name": "form_id", "value": "historical_dam_storage_form"})
    form = form_id_input.find_parent("form") if form_id_input else (soup.find("form", id=re.compile("historical", re.I)) or soup.find("form"))
    if not form:
        raise RuntimeError("Seqwater historical form was not found")
    body: dict[str, str] = {}
    for element in form.select("input[name]"):
        body[element.get("name")] = element.get("value", "")
    today = datetime.now(BRISBANE).date()
    body.update({
        "start_date": str(today - timedelta(days=days)), "end_date": str(today),
        "form_id": body.get("form_id") or "historical_dam_storage_form",
        "_triggering_element_name": "start_date", "_drupal_ajax": "1",
    })
    # Drupal's AJAX library state is sometimes a hidden form input and sometimes
    # only present in drupalSettings. Carry it across when available.
    if "ajax_page_state[libraries]" not in body:
        m = re.search(r'ajax_page_state\[libraries\]["\']?\s*[:=]\s*["\']([^"\']+)', page.text)
        if m:
            body["ajax_page_state[libraries]"] = m.group(1)
    body.setdefault("ajax_page_state[theme]", "seqwater")
    body.setdefault("ajax_page_state[theme_token]", "")
    response = session.post(SEQ_HISTORY_URL, params={"ajax_form": "1", "_wrapper_format": "drupal_ajax"},
                            data=body, headers={"Accept": "application/json, text/javascript, */*; q=0.01",
                                                "X-Requested-With": "XMLHttpRequest", "Referer": SEQ_HISTORY_URL}, timeout=90)
    response.raise_for_status()
    payload = response.json()
    historical = find_nested_historical(payload)
    if not historical:
        raise RuntimeError("Seqwater historical data was not present in the AJAX response")
    result: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for graph in historical:
        data_rows = graph.get("data") or []
        # Use series metadata if it provides source fields; fixed mapping is a
        # validated fallback extracted from the supplied Power BI report.
        field_map = dict(SEQ_HISTORY_FIELDS)
        for series in graph.get("series") or []:
            if not isinstance(series, dict):
                continue
            source = str(series.get("source") or "")
            m = re.search(r"p(\d+)", source)
            dam = registry.match(series.get("name"), "Seqwater")
            if m and dam:
                field_map[int(m.group(1))] = dam["source_name"]
        for row in data_rows:
            if not isinstance(row, dict):
                continue
            observed = iso_datetime(row.get("ds") or row.get("d"))
            if not observed:
                continue
            for idx, source_name in field_map.items():
                dam = registry.match(source_name, "Seqwater")
                if not dam:
                    continue
                pct, vol = number(row.get(f"p{idx}")), number(row.get(f"l{idx}"))
                if pct is None and vol is None:
                    continue
                result[dam["id"]].append({
                    "observed_at": observed, "percent_full": pct, "volume_ml": vol,
                    "storage_level_m": None, "outflow_cms": None, "rainfall_mm": None, "river_level_m": None,
                    "source": "Seqwater", "quality_status": "live",
                })
    if len(result) < 20:
        raise RuntimeError(f"Seqwater history parser returned only {len(result)} dam series")
    return result


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*r*math.atan2(math.sqrt(a), math.sqrt(1-a))


def extract_monitoring_sites(session: requests.Session) -> list[dict[str, Any]]:
    response = session.get(QLD_MONITORING_SITES, timeout=120)
    response.raise_for_status()
    root = ET.fromstring(response.content)
    sites: list[dict[str, Any]] = []
    for element in root.iter():
        attrs = {k.lower(): v for k, v in element.attrib.items()}
        station = attrs.get("station") or attrs.get("stationno") or attrs.get("stnnum") or attrs.get("site") or attrs.get("siteid") or attrs.get("stn")
        short = attrs.get("shortname") or attrs.get("name") or attrs.get("description")
        lat, lon = number(attrs.get("latdec") or attrs.get("latitude")), number(attrs.get("lngdec") or attrs.get("longitude"))
        if station and short:
            sites.append({"station": station, "name": short, "latitude": lat, "longitude": lon,
                          "group": attrs.get("grpvalsdesc") or attrs.get("grpvals") or ""})
    # Some XML variants put data in child text rather than attributes.
    if not sites:
        for element in root.findall(".//*"):
            values = {child.tag.split("}")[-1].lower(): clean_text(child.text) for child in list(element)}
            station = values.get("station") or values.get("stationno") or values.get("stnnum") or values.get("siteid")
            short = values.get("shortname") or values.get("name")
            if station and short:
                sites.append({"station": station, "name": short,
                              "latitude": number(values.get("latdec") or values.get("latitude")),
                              "longitude": number(values.get("lngdec") or values.get("longitude")), "group": values.get("basin", "")})
    if not sites:
        raise RuntimeError("Queensland monitoring station registry contained no parseable sites")
    return sites


def station_score(dam: dict[str, Any], site: dict[str, Any]) -> float:
    dkeys = [norm(x) for x in dam.get("aliases", []) + [dam["name"], dam.get("source_name")]]
    skey = norm(site["name"])
    score = 0.0
    for key in dkeys:
        if not key:
            continue
        if skey == key:
            score = max(score, 120)
        elif key in skey:
            score = max(score, 90 + min(len(key), 20))
        elif skey in key and len(skey) > 6:
            score = max(score, 75)
    words = {w for a in dam.get("aliases", []) + [dam["name"]] for w in re.findall(r"[a-z0-9]+", a.lower()) if len(w) > 3 and w not in {"dam", "falls", "lake"}}
    score += 6 * sum(1 for w in words if w in site["name"].lower())
    lname = site["name"].lower()
    if "dam" in lname or "headwater" in lname or "head water" in lname:
        score += 15
    if site.get("latitude") is not None and site.get("longitude") is not None:
        distance = haversine_km(dam["latitude"], dam["longitude"], site["latitude"], site["longitude"])
        score += max(0, 20-distance)
        if distance > 80:
            score -= 30
    return score


def discover_sunwater_codes(session: requests.Session, registry: Registry, sites: list[dict[str, Any]]) -> dict[str, str]:
    discovered = {d["id"]: str(d["station_code"]) for d in registry.dams if d.get("operator") == "Sunwater" and d.get("station_code")}
    # First preference: official Queensland monitoring registry, matched by name
    # and geography. The API uses those same station identifiers for known dams.
    for dam in (d for d in registry.dams if d["operator"] == "Sunwater" and d["id"] not in discovered):
        candidates = sorted(((station_score(dam, s), s) for s in sites), key=lambda x: x[0], reverse=True)
        if candidates and candidates[0][0] >= 80:
            discovered[dam["id"]] = str(candidates[0][1]["station"])
    # Second preference: inspect official Sunwater HTML/scripts for API URLs or
    # station codes near a dam name. This catches any identifier not present in
    # the public monitoring registry.
    pages: list[str] = []
    for url in (SUN_HISTORY_PAGE, SUN_DAMS_URL):
        try:
            r = session.get(url, timeout=50); r.raise_for_status(); pages.append(r.text)
        except Exception as exc:
            LOG.warning("Could not inspect %s for station codes: %s", url, exc)
    joined = "\n".join(pages)
    api_pairs = re.findall(r"(?:storagecapacity|Sites)/([0-9]{5,8}[A-Z]?)", joined, re.I)
    for dam in (d for d in registry.dams if d["operator"] == "Sunwater" and d["id"] not in discovered):
        best: tuple[int, str] | None = None
        for alias in dam.get("aliases", []) + [dam["name"]]:
            for match in re.finditer(re.escape(alias), joined, re.I):
                nearby = joined[max(0, match.start()-600):match.end()+600]
                for code in re.findall(r"\b[0-9]{5,8}[A-Z]?\b", nearby):
                    distance = abs(nearby.lower().find(code.lower()) - nearby.lower().find(alias.lower()))
                    candidate = (1000-distance, code)
                    if best is None or candidate > best:
                        best = candidate
        if best and best[0] > 200:
            discovered[dam["id"]] = best[1]
        elif len(api_pairs) == 1 and dam["name"] == "Burdekin Falls Dam":
            discovered[dam["id"]] = api_pairs[0]
    return discovered


def sunwater_station_candidates(dam: dict[str, Any], sites: list[dict[str, Any]]) -> list[str]:
    """Return plausible storage station identifiers in descending confidence."""
    ranked: list[tuple[float, str]] = []
    for site in sites:
        code = str(site.get("station") or "").strip()
        if not code or not re.fullmatch(r"[0-9]{5,8}[A-Z]?", code, re.I):
            continue
        score = station_score(dam, site)
        if score >= 75:
            ranked.append((score, code))
    result: list[str] = []
    for _, code in sorted(ranked, reverse=True):
        if code not in result:
            result.append(code)
    return result


def fetch_sunwater_current_api(session: requests.Session, station: str, dam_id: str) -> dict[str, Any]:
    response = session.get(f"{SUN_API_ROOT}/storagecapacity/{station}/current", timeout=40)
    response.raise_for_status()
    value = response.json()
    return {
        "dam_id": dam_id, "observed_at": iso_datetime_sunwater(value.get("date")),
        "percent_full": number(value.get("percentageFull")), "volume_ml": number(value.get("megaLitres")),
        "full_supply_volume_ml": number(value.get("totalCapacityMegaLitres")), "storage_level_m": None,
        "outflow_cms": None, "rainfall_mm": None, "river_level_m": None, "information": None,
        "source": "Sunwater", "retrieved_at": now_iso(), "quality_status": "live", "station_code": station,
    }


def parse_sunwater_current_page(session: requests.Session, registry: Registry) -> dict[str, dict[str, Any]]:
    response = session.get(SUN_DAMS_URL, timeout=50)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    results: dict[str, dict[str, Any]] = {}
    # Search cards/containers first.
    for text_node in soup.find_all(string=re.compile(r"Dam", re.I)):
        dam = registry.match(text_node, "Sunwater")
        if not dam:
            continue
        parent = text_node.parent
        for _ in range(5):
            if not parent: break
            text = clean_text(parent.get_text(" ", strip=True))
            m = re.search(r"(-?\d+(?:\.\d+)?)\s*%", text)
            if m:
                results[dam["id"]] = {
                    "dam_id": dam["id"], "observed_at": None, "percent_full": float(m.group(1)),
                    "volume_ml": None, "full_supply_volume_ml": None, "storage_level_m": None,
                    "outflow_cms": None, "rainfall_mm": None, "river_level_m": None, "information": None,
                    "source": "Sunwater", "retrieved_at": now_iso(), "quality_status": "live-page",
                }
                break
            parent = parent.parent
    # Search JSON/inline-script contexts as a fallback.
    raw = response.text
    for dam in (d for d in registry.dams if d["operator"] == "Sunwater" and d["id"] not in results):
        for alias in dam.get("aliases", []) + [dam["name"]]:
            m = re.search(re.escape(alias) + r".{0,800}?(\d+(?:\.\d+)?)\s*%", raw, re.I | re.S)
            if m:
                results[dam["id"]] = {
                    "dam_id": dam["id"], "observed_at": None, "percent_full": float(m.group(1)),
                    "volume_ml": None, "full_supply_volume_ml": None, "storage_level_m": None,
                    "outflow_cms": None, "rainfall_mm": None, "river_level_m": None, "information": None,
                    "source": "Sunwater", "retrieved_at": now_iso(), "quality_status": "live-page",
                }
                break
    return results


def fetch_sunwater_history(session: requests.Session, station: str, days: int) -> list[dict[str, Any]]:
    start = (datetime.now(timezone.utc) - timedelta(days=days)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    token: str | int | None = 1
    seen_tokens: set[str] = set()
    records: list[dict[str, Any]] = []
    for _ in range(200):
        params = {"startDate": start, "continuationToken": token}
        response = session.get(f"{SUN_API_ROOT}/Sites/{station}/data", params=params, timeout=60)
        response.raise_for_status()
        payload = response.json()
        values = payload.get("value") or []
        for value in values:
            observed = iso_datetime_sunwater(value.get("date"))
            if not observed:
                continue
            records.append({
                "observed_at": observed, "percent_full": number(value.get("percentageFull")),
                "volume_ml": number(value.get("volumeMegaLitres")), "storage_level_m": number(value.get("storageLevelMetres")),
                "outflow_cms": number(value.get("cubicMetersPerSecond")), "rainfall_mm": number(value.get("rainfallMillimetres")),
                "river_level_m": number(value.get("riverLevelMetres")), "source": "Sunwater", "quality_status": "live",
            })
        new_token = payload.get("continuationToken")
        if not values or new_token in (None, "", 0, "0"):
            break
        token_key = str(new_token)
        if token_key in seen_tokens or token_key == str(token):
            break
        seen_tokens.add(token_key)
        token = new_token
    return records


def parse_bom_bulletin_page(html: str, url: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    records: list[dict[str, Any]] = []
    for row in soup.select("table.tabledata tr, .tabledata tr"):
        cells = [clean_text(c.get_text(" ", strip=True)) for c in row.find_all(["td", "th"])]
        if len(cells) < 4 or cells[0].lower() in {"station name", "station"}:
            continue
        height = number(cells[3])
        if not cells[0] or height is None:
            continue
        records.append({"name": cells[0], "station_type": cells[1] if len(cells)>1 else None,
                        "time_day": cells[2] if len(cells)>2 else None, "height_m": height,
                        "gauge_datum": cells[4] if len(cells)>4 else None, "tendency": cells[5] if len(cells)>5 else None,
                        "crossing_m": number(cells[6]) if len(cells)>6 else None,
                        "flood_classification": cells[7] if len(cells)>7 else None, "bulletin_url": url})
    return records


def fetch_bom_bulletins(session: requests.Session) -> list[dict[str, Any]]:
    response = session.get(BOM_RIVER_INDEX, timeout=50)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    urls: set[str] = set()
    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]
        if "wrap_fwo.pl" in href and "IDQ" in href:
            urls.add(urljoin(BOM_RIVER_INDEX, href).split("#", 1)[0])
    # Include the two verified report pages even if the index layout changes.
    urls.update({
        "https://www.bom.gov.au/cgi-bin/wrap_fwo.pl?IDQ60286.html",
        "https://www.bom.gov.au/cgi-bin/wrap_fwo.pl?IDQ60290.html",
    })
    records: list[dict[str, Any]] = []
    for url in sorted(urls):
        try:
            r = session.get(url, timeout=35); r.raise_for_status(); records.extend(parse_bom_bulletin_page(r.text, url))
        except Exception as exc:
            LOG.warning("BOM bulletin failed: %s: %s", url, exc)
    return records


def match_current_gauge(name: str, bulletin_records: list[dict[str, Any]]) -> dict[str, Any] | None:
    key = norm(name)
    candidates = []
    for record in bulletin_records:
        rkey = norm(record["name"])
        if not rkey:
            continue
        score = 100 if rkey == key else 80 if key in rkey or rkey in key else 0
        if score:
            candidates.append((score - abs(len(rkey)-len(key)), record))
    return max(candidates, default=(0, None), key=lambda x: x[0])[1]


def build_gauges(registry: Registry, sites: list[dict[str, Any]], bulletin_records: list[dict[str, Any]],
                 overrides: dict[str, list[dict[str, Any]]]) -> dict[str, list[dict[str, Any]]]:
    output: dict[str, list[dict[str, Any]]] = {}
    for dam in registry.dams:
        chosen = [copy.deepcopy(x) for x in overrides.get(dam["id"], [])]
        existing_names = {norm(x.get("name")) for x in chosen}
        # Exact dam/headwater/tailwater sites are high confidence. Otherwise add
        # only one nearby candidate and label it explicitly as proximity-based.
        ranked: list[tuple[float, float, dict[str, Any]]] = []
        for site in sites:
            if site.get("latitude") is None or site.get("longitude") is None:
                continue
            distance = haversine_km(dam["latitude"], dam["longitude"], site["latitude"], site["longitude"])
            if distance > 60:
                continue
            score = station_score(dam, site)
            ranked.append((score, distance, site))
        ranked.sort(key=lambda x: (-x[0], x[1]))
        high = [(score, dist, site) for score, dist, site in ranked if score >= 75][:3]
        candidates = high or ranked[:1]
        for score, distance, site in candidates:
            if norm(site["name"]) in existing_names:
                continue
            confidence = "high" if score >= 90 else "candidate"
            relationship = "dam or associated gauge" if score >= 75 else "nearby gauge — relationship not verified"
            chosen.append({
                "id": str(site["station"]), "name": site["name"], "relationship": relationship,
                "confidence": confidence, "distance_km": round(distance, 1), "latitude": site.get("latitude"),
                "longitude": site.get("longitude"), "image_url": None, "bulletin_url": None,
            })
            existing_names.add(norm(site["name"]))
        for gauge in chosen:
            current = match_current_gauge(gauge.get("name", ""), bulletin_records)
            if current:
                gauge["current"] = {k:v for k,v in current.items() if k != "name"}
                gauge["bulletin_url"] = gauge.get("bulletin_url") or current.get("bulletin_url")
        if chosen:
            output[dam["id"]] = chosen
    return output


def merge_history(dam_id: str, new_records: Iterable[dict[str, Any]], max_days: int = 3650, compact_sunwater: bool = False) -> list[dict[str, Any]]:
    path = HISTORY / f"{dam_id}.json"
    old = read_json(path, {"observations": []}).get("observations", [])
    merged: dict[str, dict[str, Any]] = {}
    for record in list(old) + list(new_records):
        stamp = record.get("observed_at")
        if stamp:
            merged[stamp] = {**merged.get(stamp, {}), **record}
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=max_days)
    parsed: list[tuple[datetime, dict[str, Any]]] = []
    for stamp, record in merged.items():
        try:
            dt = date_parser.parse(stamp)
            if dt.tzinfo is None: dt = dt.replace(tzinfo=BRISBANE)
            dt = dt.astimezone(timezone.utc)
            if dt < cutoff or dt > now + timedelta(days=2): continue
        except Exception:
            continue
        parsed.append((dt, record))
    parsed.sort(key=lambda x: x[0])
    if compact_sunwater:
        # Sunwater can publish many sub-hourly records. Preserve all detail for
        # seven days, one record per three-hour bucket to 90 days, and one per
        # day thereafter. This keeps the GitHub Pages repository sustainable.
        buckets: dict[tuple[Any, ...], tuple[datetime, dict[str, Any]]] = {}
        for dt, record in parsed:
            age = now - dt
            if age <= timedelta(days=7):
                key = ("raw", record["observed_at"])
            elif age <= timedelta(days=90):
                key = ("3h", dt.year, dt.month, dt.day, dt.hour // 3)
            else:
                key = ("day", dt.year, dt.month, dt.day)
            buckets[key] = (dt, record)
        parsed = sorted(buckets.values(), key=lambda x: x[0])
    output = [record for _, record in parsed]
    write_json(path, {"dam_id": dam_id, "observations": output})
    return output


def sunwater_history_days(dam_id: str, requested_days: int) -> int:
    """Use a 30-day first backfill, then a small overlapping incremental fetch."""
    existing = read_json(HISTORY / f"{dam_id}.json", {"observations": []}).get("observations", [])
    live_dates = []
    for item in existing:
        if item.get("source") != "Sunwater" or item.get("quality_status") != "live":
            continue
        try:
            dt = date_parser.parse(item["observed_at"])
            if dt.tzinfo is None: dt = dt.replace(tzinfo=BRISBANE)
            utc = dt.astimezone(timezone.utc)
            if utc <= datetime.now(timezone.utc) + timedelta(days=2):
                live_dates.append(utc)
        except Exception:
            pass
    if not live_dates:
        return max(3, min(requested_days, 30))
    missing = (datetime.now(timezone.utc) - max(live_dates)).total_seconds() / 86400
    return max(3, min(30, math.ceil(missing) + 2))


def closest_delta(observations: list[dict[str, Any]], current: float | None, observed_at: str | None, days: int) -> float | None:
    if current is None or not observed_at:
        return None
    try:
        newest = date_parser.parse(observed_at)
        if newest.tzinfo is None: newest = newest.replace(tzinfo=BRISBANE)
    except Exception:
        return None
    target = newest - timedelta(days=days)
    candidates = []
    for item in observations:
        pct = number(item.get("percent_full"))
        stamp = iso_datetime(item.get("observed_at"))
        if pct is None or not stamp: continue
        dt = date_parser.parse(stamp)
        candidates.append((abs((dt-target).total_seconds()), pct))
    if not candidates: return None
    distance, prior = min(candidates)
    tolerance = max(36*3600, days*.35*86400)
    return round(current-prior, 2) if distance <= tolerance else None


def stale(observed_at: str | None, hours: int = 48) -> bool:
    if not observed_at: return True
    try:
        dt = date_parser.parse(observed_at)
        if dt.tzinfo is None: dt = dt.replace(tzinfo=BRISBANE)
        return datetime.now(timezone.utc) - dt.astimezone(timezone.utc) > timedelta(hours=hours)
    except Exception:
        return True


def run(history_days: int) -> int:
    started = now_iso()
    session = make_session()
    dams = read_json(CONFIG / "dams.json", [])
    if not dams:
        raise RuntimeError("config/dams.json is missing or empty")
    registry = Registry(dams)
    previous_latest = {x["dam_id"]: x for x in read_json(DATA / "latest.json", {"dams": []}).get("dams", [])}
    current = copy.deepcopy(previous_latest)
    health: dict[str, Any] = {"generated_at": started, "overall_status": "ok", "providers": {}}

    # Seqwater current
    try:
        records = parse_seqwater_current(session, registry)
        for item in records: current[item["dam_id"]] = item
        seq_status = "ok" if len(records) >= 25 else "partial"
        health["providers"]["seqwater_current"] = health_record(seq_status, records=len(records), expected_records=25, url=SEQ_CURRENT_URL)
    except Exception as exc:
        LOG.exception("Seqwater current failed")
        health["providers"]["seqwater_current"] = health_record("failed", message=str(exc), retained_previous=True)

    # Seqwater history
    try:
        histories = parse_seqwater_history(session, registry, history_days)
        for dam_id, records in histories.items(): merge_history(dam_id, records)
        health["providers"]["seqwater_historical"] = health_record("ok", dams=len(histories), observations=sum(map(len, histories.values())), url=SEQ_HISTORY_URL)
    except Exception as exc:
        LOG.exception("Seqwater history failed")
        health["providers"]["seqwater_historical"] = health_record("failed", message=str(exc), retained_previous=True)

    # Station registry supports both Sunwater code discovery and gauge mapping.
    sites: list[dict[str, Any]] = []
    try:
        sites = extract_monitoring_sites(session)
        health["providers"]["qld_station_registry"] = health_record("ok", records=len(sites), url=QLD_MONITORING_SITES)
    except Exception as exc:
        LOG.exception("Queensland station registry failed")
        health["providers"]["qld_station_registry"] = health_record("failed", message=str(exc))

    # Configured station codes remain preferred until a candidate is proven by a
    # successful API response. This prevents a nearby monitoring station from
    # being persisted merely because its name is similar to a dam.
    codes = discover_sunwater_codes(session, registry, sites)
    changed_registry = False

    # Sunwater current. Page values are a fallback; API values replace them.
    page_values: dict[str, dict[str, Any]] = {}
    try:
        page_values = parse_sunwater_current_page(session, registry)
    except Exception as exc:
        LOG.warning("Sunwater page fallback failed: %s", exc)
    sun_ok, sun_failed = 0, []
    for dam in (d for d in dams if d["operator"] == "Sunwater"):
        preferred = codes.get(dam["id"])
        candidates = ([preferred] if preferred else []) + sunwater_station_candidates(dam, sites)
        candidates = list(dict.fromkeys(c for c in candidates if c))
        last_error: Exception | None = None
        item = None
        for code in candidates[:12]:
            try:
                item = fetch_sunwater_current_api(session, code, dam["id"])
                codes[dam["id"]] = code
                if dam.get("station_code") != code:
                    dam["station_code"] = code
                    changed_registry = True
                break
            except Exception as exc:
                last_error = exc
        if item is not None:
            current[dam["id"]] = item; sun_ok += 1
        elif dam["id"] in page_values:
            fallback = {**current.get(dam["id"], {}), **{k:v for k,v in page_values[dam["id"]].items() if v is not None}}
            current[dam["id"]] = fallback; sun_ok += 1
        else:
            sun_failed.append({"dam_id": dam["id"], "message": str(last_error or "station code unresolved")})
    if changed_registry:
        write_json(CONFIG / "dams.json", dams)
        registry = Registry(dams)
    sun_status = "ok" if sun_ok == 20 else "partial" if sun_ok else "failed"
    health["providers"]["sunwater_current"] = health_record(sun_status, records=sun_ok, resolved_station_codes=len(codes), failures=sun_failed[:20], url=SUN_DAMS_URL)

    # Sunwater history. Failures are per-dam and never erase previous history.
    hist_ok, hist_failed, hist_count = 0, [], 0
    for dam in (d for d in dams if d["operator"] == "Sunwater"):
        code = codes.get(dam["id"])
        if not code:
            hist_failed.append({"dam_id": dam["id"], "message": "station code unresolved"}); continue
        try:
            fetch_days = sunwater_history_days(dam["id"], history_days)
            records = fetch_sunwater_history(session, code, fetch_days)
            merge_history(dam["id"], records, max_days=1825, compact_sunwater=True)
            hist_ok += 1; hist_count += len(records)
        except Exception as exc:
            hist_failed.append({"dam_id": dam["id"], "message": str(exc)})
    hist_status = "ok" if hist_ok == 20 else "partial" if hist_ok else "failed"
    health["providers"]["sunwater_historical"] = health_record(hist_status, dams=hist_ok, observations=hist_count, failures=hist_failed[:20], url=SUN_HISTORY_PAGE)

    # Gauges: verified overrides + station candidates + current BOM bulletin data.
    overrides = read_json(CONFIG / "gauges_overrides.json", {})
    bulletins: list[dict[str, Any]] = []
    try:
        bulletins = fetch_bom_bulletins(session)
        gauge_map = build_gauges(registry, sites, bulletins, overrides)
        write_json(DATA / "gauges.json", {"generated_at": started, "dams": gauge_map})
        verified = sum(1 for values in gauge_map.values() for x in values if x.get("confidence") == "verified")
        candidates = sum(1 for values in gauge_map.values() for x in values if x.get("confidence") != "verified")
        health["providers"]["bom_gauges"] = health_record("ok", bulletin_records=len(bulletins), verified_mappings=verified, automatic_candidates=candidates, url=BOM_RIVER_INDEX)
    except Exception as exc:
        LOG.exception("BOM gauges failed")
        health["providers"]["bom_gauges"] = health_record("failed", message=str(exc), retained_previous=True)

    # Ensure every configured dam has a latest row and calculate derived fields.
    output = []
    for dam in dams:
        item = copy.deepcopy(current.get(dam["id"], {"dam_id":dam["id"], "source":dam["operator"], "quality_status":"missing"}))
        observations = read_json(HISTORY / f"{dam['id']}.json", {"observations":[]}).get("observations", [])
        # The Sunwater current-capacity endpoint omits elevation, outflow and
        # rainfall. Carry the newest non-future historical metrics into the latest
        # row when they are recent enough to represent the same operating state.
        valid_history = []
        now_utc = datetime.now(timezone.utc)
        for observation in observations:
            try:
                dt = date_parser.parse(observation.get("observed_at", ""))
                if dt.tzinfo is None: dt = dt.replace(tzinfo=BRISBANE)
                dt = dt.astimezone(timezone.utc)
                if dt <= now_utc + timedelta(days=2): valid_history.append((dt, observation))
            except Exception:
                pass
        if valid_history:
            history_dt, history_latest = max(valid_history, key=lambda pair: pair[0])
            if now_utc - history_dt <= timedelta(hours=48):
                for metric in ("storage_level_m", "outflow_cms", "rainfall_mm", "river_level_m"):
                    if item.get(metric) is None and history_latest.get(metric) is not None:
                        item[metric] = history_latest.get(metric)
                item["supplemental_observed_at"] = history_latest.get("observed_at")
        pct = number(item.get("percent_full"))
        item["change_24h"] = closest_delta(observations, pct, item.get("observed_at"), 1)
        item["change_7d"] = closest_delta(observations, pct, item.get("observed_at"), 7)
        item["is_stale"] = stale(item.get("observed_at"))
        item["is_spilling"] = pct is not None and pct >= 100
        output.append(item)
    output.sort(key=lambda x: x["dam_id"])
    write_json(DATA / "latest.json", {"generated_at": started, "mode": "live", "dams": output})
    write_json(DATA / "dams.json", {"generated_at": started, "dams": dams})

    statuses = [p.get("status") for p in health["providers"].values()]
    required = [health["providers"].get("seqwater_current", {}).get("status"), health["providers"].get("sunwater_current", {}).get("status")]
    health["overall_status"] = "failed" if all(x == "failed" for x in required) else "partial" if any(x in {"failed", "partial"} for x in statuses) else "ok"
    health["message"] = "All live sources updated." if health["overall_status"] == "ok" else "One or more sources were incomplete; previous good data was retained where available."
    write_json(DATA / "provider_health.json", health)
    LOG.info("Completed: overall=%s", health["overall_status"])
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--history-days", type=int, default=400, help="Rolling live history window fetched on each run")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        return run(max(30, min(args.history_days, 3650)))
    except Exception:
        LOG.exception("Collector terminated before it could write provider health")
        return 2

if __name__ == "__main__":
    sys.exit(main())
