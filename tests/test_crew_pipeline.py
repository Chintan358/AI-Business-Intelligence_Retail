"""
End-to-end test of the CrewAI pipeline WITHOUT a paid LLM.

A scripted LLM stands in for Gemini/OpenAI. It still goes through CrewAI's real
agent loop (tool call -> observation -> final answer), so this verifies:
  * a real sequential Crew runs and agents call their database tools
  * context is passed between agents
  * the numeric audit catches a wrong number and sends the report back
  * recommendations with bad evidence are corrected before approval
  * only verified recommendations reach the human-approval queue
  * a missing LLM fails loudly instead of producing canned text
"""
import json
import os
import re
import tempfile

_DB = os.path.join(tempfile.gettempdir(), "crew_pipeline_test.db")
if os.path.exists(_DB):
    os.remove(_DB)
os.environ["DATABASE_URL"] = f"sqlite:///{_DB}"

import pytest  # noqa: E402
from crewai.llms.base_llm import BaseLLM  # noqa: E402

from backend.database import Base, SessionLocal, engine  # noqa: E402
from backend.models import (  # noqa: E402
    AgentLog, AnalysisSession, ApprovalRequest, StrategicRecommendation, User,
)
from backend.services.ingestion_service import seed_database_from_excel  # noqa: E402
import backend.agents.crew_runner as runner  # noqa: E402

STATE = {"calls": [], "bad_marketing_served": False, "bad_strategy_served": False}

TOOL_FOR = {
    "Principal Retail Data Analyst": "get_executive_kpis",
    "Chief Retail Marketing Strategist": "get_customer_segments",
    "Retail Financial Controller": "get_executive_kpis",
    "VP of Retail Supply Chain": "get_stockout_risks",
    "Principal Management Turnaround Consultant": "get_executive_kpis",
    "Chief Audit & Verification Inspector": "get_executive_kpis",
}


def _describe_rows(rows):
    out = []
    for r in rows[:6]:
        parts = []
        for k, v in r.items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                if any(w in k for w in ("revenue", "aov", "price", "cost")):
                    parts.append(f"{k} is ₹{v:,.2f}")
                elif k.endswith("pct"):
                    parts.append(f"{k} is {v}%")
                else:
                    parts.append(f"{k} is {v:,}")
            else:
                parts.append(f"{k} {v}")
        out.append("; ".join(parts) + ".")
    return "\n".join(out)


class ScriptedLLM(BaseLLM):
    def supports_function_calling(self) -> bool:
        return False

    def get_context_window_size(self) -> int:
        return 100000

    def call(self, messages, tools=None, callbacks=None, available_functions=None,
             from_task=None, from_agent=None, response_model=None):
        msgs = [messages] if isinstance(messages, str) else messages
        full = "\n".join(str(m.get("content", "")) for m in msgs if isinstance(m, dict))
        system = str(msgs[0].get("content", "")) if msgs and isinstance(msgs[0], dict) else full
        role = next((r for r in TOOL_FOR if r in system), None)
        STATE["calls"].append(role)

        # CrewAI appends the tool result inside the assistant message ("... Observation: <json>")
        obs_msgs = [str(m["content"]) for m in msgs
                    if isinstance(m, dict) and m.get("role") == "assistant" and "Observation:" in str(m["content"])]
        if not obs_msgs:  # step 1: every agent must use its tool first
            return (f"Thought: I need real data first.\nAction: {TOOL_FOR[role]}\n"
                    f"Action Input: {{}}")

        obs_txt = obs_msgs[-1].split("Observation:", 1)[1].strip()
        start = min(i for i in (obs_txt.find("{"), obs_txt.find("[")) if i != -1)
        obs, _ = json.JSONDecoder().raw_decode(obs_txt[start:])
        final = "Thought: I now know the final answer\nFinal Answer: "

        if role == "Principal Retail Data Analyst":
            k = obs
            return final + (
                f"Net revenue is ₹{k['net_revenue']:,.2f} from {k['completed_orders']:,} completed orders. "
                f"Gross profit is ₹{k['gross_profit']:,.2f}, a margin of {k['gross_profit_margin_pct']}%. "
                f"Operating expenses are ₹{k['total_operating_expenses']:,.2f}. "
                f"The order return rate is {k['order_return_rate_pct']}%.")
        if role == "Retail Financial Controller":
            k = obs
            return final + (
                f"Operating expenses total ₹{k['total_operating_expenses']:,.2f} against gross profit of "
                f"₹{k['gross_profit']:,.2f}. Cost of goods sold is ₹{k['cogs']:,.2f}.")
        if role == "Chief Retail Marketing Strategist":
            text = _describe_rows(obs)
            if "UNVERIFIED NUMBERS" not in full and not STATE["bad_marketing_served"]:
                STATE["bad_marketing_served"] = True  # planted hallucination
                text += " The repeat purchase rate is 46.14% and 739 customers were active."
            return final + text
        if role == "VP of Retail Supply Chain":
            return final + _describe_rows(obs)
        if role == "Principal Management Turnaround Consultant":
            k = obs
            net = k["net_revenue"]
            if "Your previous strategy failed" not in full and not STATE["bad_strategy_served"]:
                STATE["bad_strategy_served"] = True
                net = round(net * 1.2, 2)  # planted wrong evidence
            return final + json.dumps({
                "executive_summary": "Revenue is healthy but profitability needs work.",
                "growth_opportunities": ["Grow wholesale"],
                "business_risks": ["High order leakage"],
                "improvement_plan": [{"phase": "Days 1-30", "actions": ["Review returns"], "owner": "Ops"}],
                "recommendations": [
                    {"title": "Reduce order leakage", "category": "Operations",
                     "description": "Tighten return policy (target to be set by management).",
                     "expected_roi": "Estimate: recovers part of lost revenue", "risk_level": "Medium",
                     "evidence_metrics": {"order_return_rate_pct": k["order_return_rate_pct"],
                                          "net_revenue": net}},
                    {"title": "Cap marketing spend", "category": "Finance",
                     "description": "Review spend against gross profit.",
                     "expected_roi": "Estimate: lower opex", "risk_level": "Low",
                     "evidence_metrics": {"total_operating_expenses": k["total_operating_expenses"]}},
                ],
                "contradictions_resolved": [],
            })
        if role == "Chief Audit & Verification Inspector":
            return final + json.dumps({
                "verdict": "APPROVED", "confidence": "High", "unsupported_claims": [],
                "contradictions": [], "low_confidence_findings": [],
                "rationale": "Audit passed and recommendations are evidence-backed."})
        raise AssertionError("unrecognised agent")


@pytest.fixture(scope="module")
def seeded():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    user = User(email="t@example.com", hashed_password="x", full_name="T", role="manager")
    db.add(user)
    db.commit()
    seed_database_from_excel(db)
    uid = user.id
    db.close()
    return uid


def _new_session(uid):
    db = SessionLocal()
    s = AnalysisSession(user_id=uid, status="Pending")
    db.add(s)
    db.commit()
    sid = s.id
    db.close()
    return sid


def test_full_pipeline_with_audit_and_correction(seeded, monkeypatch):
    monkeypatch.setattr(runner, "get_llm", lambda: ScriptedLLM(model="scripted"))
    sid = _new_session(seeded)
    runner.run_multi_agent_analysis(sid)

    db = SessionLocal()
    s = db.query(AnalysisSession).get(sid)
    assert s.status == "Verified", s.consolidated_plan
    assert s.is_verified is True

    logs = db.query(AgentLog).filter_by(session_id=sid).order_by(AgentLog.id).all()
    assert [l.agent_name for l in logs] == [
        "Data Analyst Agent", "Marketing Agent", "Finance Agent",
        "Operations Agent", "Strategy Agent", "Verification Agent"]
    assert all(l.status == "Completed" for l in logs)
    for l in logs[:4]:  # each analyst really called a tool
        assert l.structured_data["tool_calls"], f"{l.agent_name} used no tools"

    sc = s.verification_scorecard
    assert sc["correction_rounds"] >= 1, "planted wrong number was not caught"
    assert any(c["agent"] == "marketing_agent" for c in sc["corrections"])
    assert sc["mathematical_accuracy_pct"] >= runner.MIN_AUDIT_ACCURACY
    assert sc["hallucination_count"] == 0
    assert "739" not in s.consolidated_plan["agent_results"]["marketing_agent"]

    recs = db.query(StrategicRecommendation).filter_by(session_id=sid).all()
    assert len(recs) == 2 and all(r.status == "Pending" for r in recs)
    for r in recs:  # stored evidence is the database value, not the LLM claim
        assert all(m["match"] for m in r.supporting_evidence["metrics"].values())
    assert db.query(ApprovalRequest).filter(
        ApprovalRequest.recommendation_id.in_([r.id for r in recs])).count() == 2

    from backend.models import GeneratedReport
    rep = db.query(GeneratedReport).filter_by(session_id=sid).first()
    assert rep and os.path.getsize(rep.file_path) > 5000
    db.close()


def test_fails_loudly_without_llm(seeded, monkeypatch):
    monkeypatch.setattr(runner, "get_llm", lambda: None)
    sid = _new_session(seeded)
    runner.run_multi_agent_analysis(sid)
    db = SessionLocal()
    s = db.query(AnalysisSession).get(sid)
    assert s.status == "Failed"
    assert "No LLM is configured" in s.consolidated_plan["error"]
    assert db.query(StrategicRecommendation).filter_by(session_id=sid).count() == 0
    db.close()


def test_audit_catches_wrong_numbers_unit():
    from backend.agents.verification import audit_text, build_ground_truth
    truth = build_ground_truth({"net_revenue": 109842110.21, "completed_orders": 1244,
                                "active_customers": 779, "repeat_purchase_rate_pct": 42.36,
                                "returned_orders": 645, "cancelled_orders": 611,
                                "order_return_rate_pct": 25.8, "order_cancellation_rate_pct": 24.44,
                                "returned_revenue_lost": 1.0, "cancelled_revenue_lost": 1.0,
                                "discount_amount": 1.0, "gross_revenue": 2.0, "gross_profit": 1.0,
                                "total_operating_expenses": 1.0, "repeat_customers": 330}, {})
    good = audit_text("a", "Net revenue is ₹109.84M from 1,244 orders. Repeat rate is 42.36%.", truth)
    bad = audit_text("a", "There were 739 active customers and a 46.14% repeat rate.", truth)
    assert len(good["unverified"]) == 0 and len(good["verified"]) == 3
    assert len(bad["unverified"]) == 2
    proj = audit_text("a", "We should aim to cut returns to 16% within 90 days.", truth)
    assert proj["unverified"] == [] and proj["projections"] == 1
