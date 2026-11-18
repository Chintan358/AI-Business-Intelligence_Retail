"""
Deterministic verification layer for the multi-agent pipeline.

This module deliberately has NO dependency on CrewAI or the database, so it can
be unit-tested in isolation. It is the "ground truth" side of the hallucination
control: every number an agent writes is extracted from its text and compared
against values computed by KPIService from the real dataset. The LLM-based
Verification Agent then reviews the result of this audit, it never replaces it.
"""
import json
import re
from typing import Any, Dict, List, Optional, Tuple

# --------------------------------------------------------------------------- #
# Ground truth
# --------------------------------------------------------------------------- #

# Fixed facts of the assignment (period length), not business metrics.
STATIC_FACTS = {184.0, 6.0}  # days in May 1 - Oct 31 2026, months in period


def _is_num(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _flatten_numbers(obj: Any, out: List[float]) -> None:
    if _is_num(obj):
        out.append(abs(float(obj)))
    elif isinstance(obj, dict):
        for v in obj.values():
            _flatten_numbers(v, out)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            _flatten_numbers(v, out)


def _collect_identifier_numbers(obj: Any, out: set) -> None:
    """Digits embedded in names/IDs ('Cookware Set 085', 'STR03') are labels, not metrics."""
    if isinstance(obj, str):
        for g in re.findall(r"\d+", obj):
            if len(g) >= 2:
                out.add(float(int(g)))
    elif isinstance(obj, dict):
        for v in obj.values():
            _collect_identifier_numbers(v, out)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            _collect_identifier_numbers(v, out)


def _share_values(rows: List[dict]) -> List[float]:
    """Percentage share of each row for every additive numeric column."""
    shares: List[float] = []
    if not rows or not all(isinstance(r, dict) for r in rows):
        return shares
    keys = {k for r in rows for k, v in r.items() if _is_num(v)}
    for k in keys:
        if k.endswith("_pct") or k.endswith("_rate"):
            continue
        vals = [abs(float(r[k])) for r in rows if _is_num(r.get(k))]
        total = sum(vals)
        if total > 0 and len(vals) > 1:
            shares.extend(v / total * 100 for v in vals)
    return shares


def build_ground_truth(
    executive_kpis: Dict[str, Any],
    datasets: Dict[str, Any],
    row_counts: Optional[Dict[str, int]] = None,
) -> Dict[str, Any]:
    """
    Builds the set of numbers an agent is allowed to cite.

    executive_kpis : output of KPIService.get_executive_kpis()
    datasets       : name -> list/dict output of the other KPIService methods
    row_counts     : record counts per source table (e.g. {"transactions": 2500})
    """
    values: List[float] = []
    _flatten_numbers(executive_kpis, values)
    for name, data in datasets.items():
        _flatten_numbers(data, values)
        if isinstance(data, list):
            values.extend(_share_values(data))
        elif isinstance(data, dict):
            for sub in data.values():
                if isinstance(sub, list):
                    values.extend(_share_values(sub))
    identifiers: set = set()
    for data in datasets.values():
        _collect_identifier_numbers(data, identifiers)
    if row_counts:
        values.extend(float(v) for v in row_counts.values())
        values.append(float(sum(row_counts.values())))

    # Simple, explainable derivations an analyst would legitimately quote.
    k = executive_kpis
    derived: Dict[str, float] = {}
    try:
        derived["leakage_orders"] = k["returned_orders"] + k["cancelled_orders"]
        derived["leakage_rate_pct"] = round(
            k["order_return_rate_pct"] + k["order_cancellation_rate_pct"], 2
        )
        derived["leakage_revenue"] = round(
            k["returned_revenue_lost"] + k["cancelled_revenue_lost"], 2
        )
        derived["discount_pct_of_gross"] = round(
            k["discount_amount"] / k["gross_revenue"] * 100, 2
        ) if k["gross_revenue"] else 0.0
        derived["opex_pct_of_net_revenue"] = round(
            k["total_operating_expenses"] / k["net_revenue"] * 100, 2
        ) if k["net_revenue"] else 0.0
        derived["opex_minus_gross_profit"] = round(
            k["total_operating_expenses"] - k["gross_profit"], 2
        )
        derived["non_repeat_customers"] = k["active_customers"] - k["repeat_customers"]
    except (KeyError, TypeError, ZeroDivisionError):
        pass
    values.extend(abs(v) for v in derived.values())
    values.extend(STATIC_FACTS)

    return {
        "values": sorted(set(round(v, 6) for v in values if v is not None)),
        "kpis": {kk: vv for kk, vv in executive_kpis.items() if _is_num(vv)},
        "derived": derived,
        "identifier_numbers": sorted(identifiers),
    }


# --------------------------------------------------------------------------- #
# Claim extraction
# --------------------------------------------------------------------------- #

_UNIT = {
    "cr": 1e7, "crore": 1e7, "crores": 1e7,
    "l": 1e5, "lakh": 1e5, "lakhs": 1e5, "lac": 1e5,
    "m": 1e6, "mn": 1e6, "million": 1e6,
    "k": 1e3, "thousand": 1e3,
    "b": 1e9, "bn": 1e9, "billion": 1e9,
}
_MONEY = re.compile(
    r"(?:₹|Rs\.?\s?|INR\s?)\s*(\d[\d,]*(?:\.\d+)?)\s*"
    r"(crores?|cr|lakhs?|lac|million|mn|thousand|billion|bn|[MKLB])?(?![A-Za-z])",
    re.IGNORECASE,
)
_PERCENT = re.compile(r"(\d+(?:\.\d+)?)\s?%")
_PLAIN = re.compile(r"(?<![\w.])(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d{3,}(?:\.\d+)?)(?![\w%])")

# Sentences containing these words are targets/forecasts, not claims about data.
_PROJECTION_HINTS = re.compile(
    r"\b(target|targets|aim|aims|goal|goals|should|could|would|propos\w*|recommend\w*|"
    r"project\w*|expect\w*|estimat\w*|forecast\w*|plan\w*|reduce|raise|increase|"
    r"lower|cap|achieve|improve|boost|within|by day|next|upcoming|potential)\b",
    re.IGNORECASE,
)


def _decimals(num_str: str) -> int:
    return len(num_str.split(".")[1]) if "." in num_str else 0


def _sentences(text: str) -> List[Tuple[int, int, str]]:
    spans = []
    for m in re.finditer(r"[^.\n!?]*(?:\.\d[^.\n!?]*)*[.\n!?]?", text):
        if m.group().strip():
            spans.append((m.start(), m.end(), m.group().strip()))
    return spans


def extract_claims(text: str) -> List[Dict[str, Any]]:
    """Returns numeric claims: {raw, value, tol, kind, context, projection}."""
    if not text:
        return []
    claims: List[Dict[str, Any]] = []
    masked = list(text)

    def _mask(span: Tuple[int, int]) -> None:
        for i in range(span[0], span[1]):
            masked[i] = " "

    def _context(pos: int) -> Tuple[str, bool]:
        for s, e, sent in _sentences(text):
            if s <= pos < e:
                return sent[:220], bool(_PROJECTION_HINTS.search(sent))
        return text[max(0, pos - 60): pos + 60], False

    for m in _MONEY.finditer(text):
        num = m.group(1)
        unit = (m.group(2) or "").lower()
        mult = _UNIT.get(unit, 1.0)
        value = float(num.replace(",", "")) * mult
        tol = 0.5 * 10 ** -_decimals(num) * mult + 1e-6
        ctx, proj = _context(m.start())
        claims.append({"raw": m.group().strip(), "value": value, "tol": tol,
                       "kind": "currency", "context": ctx, "projection": proj})
        _mask(m.span())

    for m in _PERCENT.finditer("".join(masked)):
        num = m.group(1)
        tol = 0.5 * 10 ** -_decimals(num) + 0.01
        ctx, proj = _context(m.start())
        claims.append({"raw": m.group().strip(), "value": float(num), "tol": tol,
                       "kind": "percent", "context": ctx, "projection": proj})
        _mask(m.span())

    for m in _PLAIN.finditer("".join(masked)):
        num = m.group(1)
        value = float(num.replace(",", ""))
        if 2000 <= value <= 2100 and "," not in num and "." not in num:
            continue  # a calendar year, not a metric
        tol = 0.5 * 10 ** -_decimals(num) + 1e-6
        ctx, proj = _context(m.start())
        claims.append({"raw": m.group().strip(), "value": value, "tol": tol,
                       "kind": "number", "context": ctx, "projection": proj})
    return claims


def _nearest(value: float, truth: List[float]) -> Tuple[float, float]:
    best = min(truth, key=lambda t: abs(t - value)) if truth else 0.0
    return best, abs(best - value)


def _matches_any(claim: Dict[str, Any], values: List[float]) -> bool:
    return _nearest(claim["value"], values)[1] <= claim["tol"]


def audit_text(agent: str, text: str, truth: Dict[str, Any]) -> Dict[str, Any]:
    """Checks every non-projection number in `text` against ground truth."""
    values = truth["values"]
    identifiers = set(truth.get("identifier_numbers", []))
    verified, unverified, projections = [], [], []
    for c in extract_claims(text):
        if (c["kind"] == "number" and "," not in c["raw"] and "." not in c["raw"]
                and c["value"] in identifiers and not _matches_any(c, values)):
            continue  # label inside a product name / store id, not a metric
        if c["projection"]:
            projections.append(c)
            continue
        nearest, diff = _nearest(c["value"], values)
        entry = {"agent": agent, "claim": c["raw"], "context": c["context"],
                 "ground_truth": nearest}
        if diff <= c["tol"]:
            verified.append({**entry, "match": True})
        else:
            unverified.append({**entry, "match": False})
    return {"verified": verified, "unverified": unverified,
            "projections": len(projections)}


def audit_reports(reports: Dict[str, str], truth: Dict[str, Any]) -> Dict[str, Any]:
    """Audits the descriptive agents' reports (data, marketing, finance, ops)."""
    verified: List[dict] = []
    unverified: List[dict] = []
    projections = 0
    per_agent: Dict[str, Dict[str, int]] = {}
    for agent, text in reports.items():
        r = audit_text(agent, text, truth)
        verified += r["verified"]
        unverified += r["unverified"]
        projections += r["projections"]
        per_agent[agent] = {"verified": len(r["verified"]),
                            "unverified": len(r["unverified"])}
    checked = len(verified) + len(unverified)
    accuracy = round(len(verified) / checked * 100, 2) if checked else 0.0
    return {
        "claims_checked": checked,
        "verified_count": len(verified),
        "unverified_count": len(unverified),
        "projections_not_scored": projections,
        "accuracy_pct": accuracy,
        "per_agent": per_agent,
        "verified_claims": verified,
        "unverified_claims": unverified,
    }


# --------------------------------------------------------------------------- #
# Recommendation evidence
# --------------------------------------------------------------------------- #

def validate_recommendation(rec: Dict[str, Any], truth: Dict[str, Any]) -> Dict[str, Any]:
    """
    Every recommendation must cite KPI evidence as {metric_key: value}.
    Each cited value is compared with the real KPI; the stored evidence keeps the
    DATABASE value, so a hallucinated number never reaches the approval screen.
    """
    evidence = rec.get("evidence_metrics")
    kpis = {**truth["kpis"], **truth["derived"]}
    result: Dict[str, Any] = {"metrics": {}, "has_evidence": False, "all_valid": False}
    if not isinstance(evidence, dict) or not evidence:
        result["reason"] = "No evidence_metrics supplied."
        return result
    result["has_evidence"] = True
    ok = True
    for key, claimed in evidence.items():
        actual = kpis.get(key)
        if actual is None or not _is_num(claimed):
            result["metrics"][key] = {"claimed": claimed, "actual": actual,
                                      "match": False, "note": "unknown metric or non-numeric"}
            ok = False
            continue
        tol = max(abs(actual) * 0.005, 0.01)  # 0.5% rounding tolerance
        match = abs(float(claimed) - float(actual)) <= tol
        result["metrics"][key] = {"claimed": claimed, "actual": actual, "match": match}
        ok = ok and match
    result["all_valid"] = ok
    return result


# --------------------------------------------------------------------------- #
# LLM output parsing
# --------------------------------------------------------------------------- #

def extract_json(text: str) -> Optional[Dict[str, Any]]:
    """Parses a JSON object out of LLM output (handles ``` fences / chatter)."""
    if not text:
        return None
    cleaned = re.sub(r"```(?:json)?", "", text).strip()
    try:
        data = json.loads(cleaned)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        pass
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start != -1 and end > start:
        try:
            data = json.loads(cleaned[start:end + 1])
            return data if isinstance(data, dict) else None
        except json.JSONDecodeError:
            return None
    return None
