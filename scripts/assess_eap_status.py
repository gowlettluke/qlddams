#!/usr/bin/env python3
"""Calculate indicative published EAP flood-trigger levels from public data.

The output is explicitly not an official activation status. It evaluates only the
published flood-operation conditions that are represented in data/eap_documents.json,
records unknown/non-public conditions, and keeps public warning status separate.
"""
from __future__ import annotations

import copy
import json
import math
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from dateutil import parser as date_parser

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
LEVEL_ORDER = {"alert": 1, "lean_forward": 2, "stand_up": 3}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return copy.deepcopy(default)


def write(path: Path, value: Any) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def num(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (TypeError, ValueError):
        return None


def parse_time(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        dt = date_parser.parse(str(value))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone(timedelta(hours=10)))
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def latest_valid_observation(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    now = datetime.now(timezone.utc)
    candidates = []
    for row in rows:
        dt = parse_time(row.get("observed_at"))
        if dt and dt <= now + timedelta(days=1):
            candidates.append((dt, row))
    return max(candidates, default=(None, None), key=lambda x: x[0] or datetime.min.replace(tzinfo=timezone.utc))[1]


def storage_trend(rows: list[dict[str, Any]]) -> tuple[str | None, float | None, float | None]:
    now = datetime.now(timezone.utc)
    parsed = []
    for row in rows:
        dt = parse_time(row.get("observed_at"))
        value = num(row.get("storage_level_m"))
        if dt and value is not None and dt <= now + timedelta(days=1):
            parsed.append((dt, value))
    parsed.sort()
    if len(parsed) < 2:
        return None, None, None
    latest_dt, latest = parsed[-1]
    eligible = [(dt, value) for dt, value in parsed[:-1] if latest_dt - dt >= timedelta(minutes=45)]
    if not eligible:
        return None, None, None
    # Prefer approximately six hours earlier; fall back to the oldest point in 24h.
    target = latest_dt - timedelta(hours=6)
    recent = [(abs((dt - target).total_seconds()), dt, value) for dt, value in eligible if latest_dt - dt <= timedelta(hours=24)]
    if recent:
        _, prior_dt, prior = min(recent)
    else:
        prior_dt, prior = eligible[-1]
    delta = latest - prior
    hours = max((latest_dt - prior_dt).total_seconds() / 3600, 1 / 60)
    rate = delta / hours
    if abs(rate) < 0.002 and abs(delta) < 0.02:
        trend = "steady"
    else:
        trend = "rising" if delta > 0 else "falling"
    return trend, round(delta, 3), round(rate, 4)


def compare(actual: Any, op: str, expected: Any) -> bool | None:
    if actual is None:
        return None
    try:
        if op == ">=": return actual >= expected
        if op == ">": return actual > expected
        if op == "<=": return actual <= expected
        if op == "<": return actual < expected
        if op == "==": return actual == expected
        if op == "!=": return actual != expected
    except TypeError:
        return None
    return None


def metric_value(metric: str, context: dict[str, Any]) -> Any:
    if metric in context:
        return context[metric]
    # Non-public/forecast/engineering metrics deliberately remain unknown.
    return None


def assess_condition(condition: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    metric = condition.get("metric")
    actual = metric_value(metric, context)
    result = compare(actual, condition.get("op", "=="), condition.get("value"))
    return {
        "metric": metric,
        "label": condition.get("label") or metric,
        "expected": condition.get("value"),
        "operator": condition.get("op", "=="),
        "actual": actual,
        "unit": condition.get("unit"),
        "proxy": bool(condition.get("proxy")),
        "publicly_observable": bool(condition.get("publicly_observable", False)),
        "result": "met" if result is True else "not_met" if result is False else "unknown",
    }


def assess_rule(rule: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    conditions = [assess_condition(c, context) for c in rule.get("conditions", [])]
    states = [c["result"] for c in conditions]
    if conditions and all(s == "met" for s in states):
        status = "met"
    elif any(s == "not_met" for s in states):
        status = "not_met"
    elif any(s == "met" for s in states) and any(s == "unknown" for s in states):
        status = "possible"
    else:
        status = "unknown"
    return {**rule, "assessment": status, "condition_results": conditions}


def confidence_for(chosen: list[dict[str, Any]], document: dict[str, Any], indication: str) -> str:
    if not chosen:
        return "indeterminate"
    conditions = [c for r in chosen for c in r.get("condition_results", [])]
    has_proxy = any(c.get("proxy") and c.get("result") == "met" for c in conditions)
    has_unknown = any(c.get("result") == "unknown" for c in conditions)
    exact_level = any(c.get("metric") == "storage_level_m" and c.get("result") == "met" for c in conditions)
    review = document.get("review_status")
    changed = document.get("document_changed") or review == "change_detected"
    expired = document.get("document_expired")
    if changed or expired:
        return "low" if indication != "unable_to_assess" else "indeterminate"
    if has_proxy:
        return "low"
    if indication in LEVEL_ORDER and exact_level and not has_unknown and review == "manually_verified":
        return "high"
    if exact_level and (has_unknown or review == "machine_extracted"):
        return "medium"
    if indication == "below_alert" and review == "manually_verified":
        return "medium"
    return "indeterminate"


def assess_one(dam: dict[str, Any], latest: dict[str, Any], history: list[dict[str, Any]], document: dict[str, Any]) -> dict[str, Any]:
    history_latest = latest_valid_observation(history) or {}
    storage_level = num(latest.get("storage_level_m"))
    if storage_level is None:
        storage_level = num(history_latest.get("storage_level_m"))
    trend, level_change, rate = storage_trend(history)
    fsl = num(document.get("fsl_m_ahd"))
    percent = num(latest.get("percent_full"))
    within_fsl = abs(storage_level - fsl) if storage_level is not None and fsl is not None else None
    context = {
        "storage_level_m": storage_level,
        "percent_full": percent,
        "storage_level_trend": trend,
        "within_operational_fsl_m": within_fsl,
        "above_operational_fsl": storage_level > fsl if storage_level is not None and fsl is not None else None,
    }

    expiry = document.get("expiry_date")
    expired = False
    if expiry:
        try:
            expired = date_parser.parse(expiry).date() < datetime.now(timezone.utc).date()
        except Exception:
            pass
    document = copy.deepcopy(document)
    document["document_expired"] = expired

    if not document.get("referable", True):
        return {
            "dam_id": dam["id"], "indication": "not_applicable", "potential_level": None,
            "confidence": "not_applicable", "formal_activation": "not_confirmed",
            "public_warning_status": "not_assessed", "reason": document.get("notes") or "No referable-dam EAP was located.",
            "storage_level_m": storage_level, "storage_level_trend": trend,
            "rules": [], "eap": document,
        }

    assessed = [assess_rule(r, context) for r in document.get("rules", []) if r.get("hazard", "flood_operations") == "flood_operations"]
    by_level = {level: [r for r in assessed if r.get("level") == level] for level in LEVEL_ORDER}
    met_levels = [level for level, rules in by_level.items() if any(r["assessment"] == "met" for r in rules)]
    possible_levels = [level for level, rules in by_level.items() if any(r["assessment"] == "possible" for r in rules)]

    chosen: list[dict[str, Any]] = []
    potential = None
    if met_levels:
        indication = max(met_levels, key=lambda x: LEVEL_ORDER[x])
        chosen = [r for r in by_level[indication] if r["assessment"] == "met"]
        reason = f"The published {indication.replace('_', ' ')} flood-trigger rule represented in the app appears to be met."
    elif possible_levels:
        potential = max(possible_levels, key=lambda x: LEVEL_ORDER[x])
        indication = "conditions_incomplete"
        chosen = [r for r in by_level[potential] if r["assessment"] == "possible"]
        reason = f"The measurable part of a published {potential.replace('_', ' ')} rule appears to be met, but one or more required conditions are unavailable or non-public."
    elif assessed and any(r["assessment"] == "not_met" for r in by_level.get("alert", [])):
        indication = "below_alert"
        chosen = [r for r in by_level["alert"] if r["assessment"] == "not_met"]
        reason = "The measurable published Alert flood threshold represented in the app does not appear to be met."
    else:
        indication = "unable_to_assess"
        chosen = [r for r in assessed if r["assessment"] == "unknown"]
        reason = "The public data does not contain enough information to assess the published flood-trigger rules."

    # Never present an old observation as a current threshold indication. Preserve
    # the threshold it would have met as a potential level, but make the current
    # assessment explicitly indeterminate until a fresh observation is available.
    source_stamp = history_latest.get("observed_at") if storage_level is not None and history_latest else latest.get("observed_at")
    source_dt = parse_time(source_stamp)
    source_stale = bool(latest.get("is_stale")) or source_dt is None or datetime.now(timezone.utc) - source_dt > timedelta(hours=48)
    if source_stale and indication in LEVEL_ORDER:
        potential = indication
        indication = "unable_to_assess"
        reason = (f"The last available reading would meet the published {potential.replace('_', ' ')} threshold represented in the app, "
                  "but the reading is stale and cannot support a current indication.")

    evidence = []
    missing = []
    for rule in chosen:
        for c in rule.get("condition_results", []):
            if c["result"] == "met":
                evidence.append(c["label"])
            elif c["result"] == "unknown":
                missing.append(c["label"])
    evidence = list(dict.fromkeys(evidence))
    missing = list(dict.fromkeys(missing))
    warnings = []
    if expired:
        warnings.append(f"The cached EAP expiry date ({expiry}) has passed; a replacement document requires review.")
    if document.get("document_changed") or document.get("review_status") == "change_detected":
        warnings.append("The official EAP document changed after the stored rules were reviewed; the rules require re-verification.")
    if source_stale:
        warnings.append("The current storage reading is stale or unavailable; no current EAP threshold indication is asserted.")
    if any(c.get("proxy") and c.get("result") == "met" for r in chosen for c in r.get("condition_results", [])):
        warnings.append("This indication uses percentage full as a low-confidence proxy because current reservoir elevation was unavailable.")

    confidence = "indeterminate" if source_stale else confidence_for(chosen, document, potential or indication)
    return {
        "dam_id": dam["id"],
        "assessed_at": now_iso(),
        "indication": indication,
        "potential_level": potential,
        "confidence": confidence,
        "formal_activation": "not_confirmed",
        "public_warning_status": "not_assessed",
        "reason": reason,
        "evidence": evidence,
        "missing_conditions": missing,
        "warnings": warnings,
        "current_percent_full": percent,
        "storage_level_m": storage_level,
        "storage_level_observed_at": history_latest.get("observed_at") if history_latest else latest.get("observed_at"),
        "storage_level_trend": trend,
        "storage_level_change_m": level_change,
        "storage_level_rate_m_per_hour": rate,
        "rules": assessed,
        "eap": {k: document.get(k) for k in (
            "referable", "document_status", "review_status", "version", "approved_date", "expiry_date",
            "document_expired", "eap_url", "emergency_info_url", "directory_url", "fsl_m_ahd",
            "notes", "stand_down_text", "sha256", "checked_at", "downloaded_at", "fetch_error")},
        "disclaimer": "Indicative comparison with published flood-operation triggers only; not a formal EAP activation level or public warning.",
    }


def main() -> int:
    dams = load(DATA / "dams.json", {"dams": []}).get("dams", [])
    latest = {x.get("dam_id"): x for x in load(DATA / "latest.json", {"dams": []}).get("dams", [])}
    documents_payload = load(DATA / "eap_documents.json", {"dams": {}})
    documents = documents_payload.get("dams", {})
    output = []
    counts: dict[str, int] = {}
    for dam in dams:
        history = load(DATA / "history" / f"{dam['id']}.json", {"observations": []}).get("observations", [])
        result = assess_one(dam, latest.get(dam["id"], {}), history, documents.get(dam["id"], {
            "dam_id": dam["id"], "referable": True, "document_status": "pending_audit", "review_status": "pending", "rules": []
        }))
        output.append(result)
        counts[result["indication"]] = counts.get(result["indication"], 0) + 1
    write(DATA / "eap_status.json", {
        "generated_at": now_iso(),
        "counts": counts,
        "formal_activation_source": "not_integrated",
        "public_warning_source": "not_integrated",
        "disclaimer": "These are indicative comparisons with published EAP flood-operation triggers. They are not formal activation levels, emergency warnings, or evacuation advice.",
        "dams": output,
    })
    print(f"Assessed {len(output)} dams: {counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
