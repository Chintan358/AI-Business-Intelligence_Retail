"""
Multi-agent execution pipeline (CrewAI).

Workflow (matches Section 7 of the project requirements)
    Phase 1  Data Analyst -> Marketing -> Finance -> Operations -> Strategy
             One CrewAI Crew, Process.sequential. Each task receives the earlier
             agents' outputs through `context`, so agents genuinely share results.
    Phase 2  Deterministic audit: every number in the analyst reports is compared
             with values computed from the database (verification.py), and every
             recommendation's cited evidence is checked against real KPIs.
    Phase 3  Correction loop: reports with unverified numbers are sent back to
             their author agent; the Strategy Agent then rebuilds the plan.
    Phase 4  Verification Agent (LLM) reviews the plan and the audit and returns
             APPROVED / REJECTED. A report is approved only if BOTH the agent and the
             deterministic audit pass.
    Phase 5  Human-in-the-loop: only verified recommendations get an
             ApprovalRequest. Nothing is executed without a manager's decision.

If no LLM is configured the session fails with a clear message. The pipeline never
substitutes canned text for agent output.
"""
import json
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from crewai import Crew, Process

from backend.agents.definitions import create_agents
from backend.agents.llm_provider import get_llm
from backend.agents.tasks import (
    create_correction_task,
    create_strategy_revision_task,
    create_tasks,
    create_verification_task,
)
from backend.agents.verification import (
    audit_reports,
    build_ground_truth,
    extract_json,
    validate_recommendation,
)
from backend.database import SessionLocal
from backend.models import (
    AgentLog,
    AnalysisSession,
    ApprovalRequest,
    GeneratedReport,
    StrategicRecommendation,
)
from backend.services.kpi_service import KPIService
from backend.services.pdf_report_service import PDFReportService

MIN_AUDIT_ACCURACY = float(os.getenv("MIN_AUDIT_ACCURACY", "90"))
MAX_CORRECTION_ROUNDS = int(os.getenv("MAX_CORRECTION_ROUNDS", "2"))
CREW_MAX_RPM = int(os.getenv("CREW_MAX_RPM", "10"))  # protects free-tier LLM quotas

# key, display name, task name (order = execution order)
PIPELINE = [
    ("data_analyst", "Data Analyst Agent", "Analyze Retail KPIs & Monthly Trajectory"),
    ("marketing_agent", "Marketing Agent", "Customer Cohorts, Retention & Channel Behaviour"),
    ("finance_agent", "Finance Agent", "Financial P&L, Operating Margin & Cost Optimization"),
    ("operations_agent", "Operations Agent", "Inventory Health, Stockouts & Product Velocity"),
    ("strategy_agent", "Strategy Agent", "Consolidated Improvement Plan & Recommendations"),
    ("verification_agent", "Verification Agent", "Numeric Audit, Hallucination Check & Approval"),
]
ANALYSIS_KEYS = [k for k, _, _ in PIPELINE[:5]]
DESCRIPTIVE_KEYS = ["data_analyst", "marketing_agent", "finance_agent", "operations_agent"]
_META = {k: (name, task) for k, name, task in PIPELINE}
VALID_CATEGORIES = {"Marketing", "Finance", "Operations", "Strategy"}
VALID_RISK = {"Low", "Medium", "High"}


class LLMNotConfiguredError(RuntimeError):
    pass


# --------------------------------------------------------------------------- #
# Execution tracking (agent-wise logs shown on the frontend monitor)
# --------------------------------------------------------------------------- #
class ExecutionTracker:
    def __init__(self, db, session_id: int, agents: dict):
        self.db = db
        self.session_id = session_id
        self.agents = agents
        self.logs: Dict[str, AgentLog] = {}
        self.started: Dict[str, float] = {}
        self.tool_calls: Dict[str, List[dict]] = {}
        self.current: Optional[str] = None

    def start(self, key: str) -> None:
        name, task = _META[key]
        log = AgentLog(
            session_id=self.session_id,
            agent_name=name,
            agent_role=self.agents[key].role,
            task_name=task,
            status="Running",
            started_at=datetime.utcnow(),
        )
        self.db.add(log)
        self.db.commit()
        self.logs[key] = log
        self.started[key] = time.time()
        self.tool_calls[key] = []
        self.current = key

    def record_tool(self, tool_name: str, tool_input: str) -> None:
        if self.current:
            self.tool_calls.setdefault(self.current, []).append(
                {"tool": tool_name, "input": tool_input[:300]}
            )

    def complete(self, key: str, output: str, structured: Optional[dict] = None) -> None:
        log = self.logs[key]
        log.status = "Completed"
        log.completed_at = datetime.utcnow()
        log.execution_duration_sec = round(time.time() - self.started[key], 2)
        log.output_text = output
        data = dict(structured or {})
        data["tool_calls"] = self.tool_calls.get(key, [])
        log.structured_data = data
        self.db.commit()

    def revise(self, key: str, output: str, correction: dict) -> None:
        """Agent re-ran after the audit; keep the history of corrections."""
        log = self.logs[key]
        data = dict(log.structured_data or {})
        data.setdefault("corrections", []).append(correction)
        data["tool_calls"] = self.tool_calls.get(key, [])
        log.output_text = output
        log.structured_data = data
        log.execution_duration_sec = round(time.time() - self.started[key], 2)
        self.db.commit()

    def fail_running(self, message: str) -> None:
        for key, log in self.logs.items():
            if log.status == "Running":
                log.status = "Failed"
                log.error_message = message[:1000]
                log.completed_at = datetime.utcnow()
                log.execution_duration_sec = round(time.time() - self.started[key], 2)
        self.db.commit()


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _snapshot(key: str, d: Dict[str, Any]) -> dict:
    """Database-derived data stored next to each agent's output (not LLM text)."""
    if key == "data_analyst":
        return {"executive_kpis": d["exec_kpis"], "monthly_trends": d["monthly"],
                "category_performance": d["category"]}
    if key == "marketing_agent":
        return {"segments": d["segments"], "channels": d["channel"],
                "repeat_rate_pct": d["exec_kpis"]["repeat_purchase_rate_pct"]}
    if key == "finance_agent":
        return {"gross_profit": d["exec_kpis"]["gross_profit"],
                "gross_margin_pct": d["exec_kpis"]["gross_profit_margin_pct"],
                "total_opex": d["exec_kpis"]["total_operating_expenses"],
                "operating_profit": d["exec_kpis"]["net_operating_profit"],
                "store_pnl": d["store"]}
    if key == "operations_agent":
        return {"stockout_alerts": d["stock_alerts"], "top_and_slow_products": d["top_slow"]}
    return {}


def _run_single(agent, task, step_cb) -> str:
    """Runs one task with one agent as its own Crew (used for corrections/verification)."""
    crew = Crew(
        agents=[agent], tasks=[task], process=Process.sequential,
        verbose=True, max_rpm=CREW_MAX_RPM, step_callback=step_cb,
    )
    return crew.kickoff().raw


def _normalise_recommendations(plan: dict) -> List[dict]:
    recs = []
    for r in (plan.get("recommendations") or [])[:6]:
        if not isinstance(r, dict) or not r.get("title") or not r.get("description"):
            continue
        category = str(r.get("category", "Strategy")).strip().title()
        risk = str(r.get("risk_level", "Medium")).strip().title()
        recs.append({
            "title": str(r["title"])[:250],
            "category": category if category in VALID_CATEGORIES else "Strategy",
            "description": str(r["description"]),
            "expected_roi": str(r.get("expected_roi", "Not quantified"))[:120],
            "risk_level": risk if risk in VALID_RISK else "Medium",
            "evidence_metrics": r.get("evidence_metrics"),
        })
    return recs


def _format_strategy_text(plan: dict) -> str:
    lines = [str(plan.get("executive_summary", "")).strip(), ""]
    for title, key in (("Growth opportunities", "growth_opportunities"),
                       ("Business risks", "business_risks")):
        items = plan.get(key) or []
        if items:
            lines.append(f"{title}:")
            lines += [f"- {i}" for i in items]
            lines.append("")
    if plan.get("improvement_plan"):
        lines.append("90-day improvement plan:")
        for ph in plan["improvement_plan"]:
            if isinstance(ph, dict):
                lines.append(f"{ph.get('phase', '')} (owner: {ph.get('owner', 'n/a')})")
                lines += [f"  - {a}" for a in ph.get("actions", [])]
    return "\n".join(lines).strip()


def _format_verification_text(sc: dict) -> str:
    lines = [
        f"FINAL VERDICT: {sc['final_verdict']}",
        f"- Numeric audit: {sc['verified_claims']} of {sc['claims_checked']} figures matched the "
        f"database ({sc['mathematical_accuracy_pct']}% accuracy; threshold {sc['accuracy_threshold_pct']}%).",
        f"- Figures that could not be verified: {sc['hallucination_count']}.",
        f"- Correction rounds used: {sc['correction_rounds']}.",
        f"- Verification Agent verdict: {sc['agent_verdict']} (confidence: {sc['agent_confidence']}).",
    ]
    for label, key in (("Unsupported claims", "unsupported_claims"),
                       ("Contradictions", "contradictions"),
                       ("Low-confidence findings", "low_confidence_findings")):
        if sc.get(key):
            lines.append(f"- {label}: " + "; ".join(map(str, sc[key])))
    if sc.get("blocked_recommendations"):
        lines.append("- Recommendations withheld from approval (evidence failed): "
                     + "; ".join(sc["blocked_recommendations"]))
    if sc.get("agent_rationale"):
        lines.append(f"- Rationale: {sc['agent_rationale']}")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Main entry point (called as a FastAPI BackgroundTask)
# --------------------------------------------------------------------------- #
def run_multi_agent_analysis(session_id: int):
    db = SessionLocal()
    session = None
    tracker: Optional[ExecutionTracker] = None
    try:
        session = db.query(AnalysisSession).filter(AnalysisSession.id == session_id).first()
        if not session:
            print(f"Session {session_id} not found.")
            return

        session.status = "Running"
        session.started_at = datetime.utcnow()
        db.commit()
        t_start = time.time()

        llm = get_llm()
        if llm is None:
            raise LLMNotConfiguredError(
                "No LLM is configured. Set GEMINI_API_KEY (and LLM_PROVIDER=gemini) or "
                "OPENAI_API_KEY on the backend and run the analysis again."
            )

        # ---- Ground truth from the database (never from the LLM) -------------
        kpi = KPIService(db)
        data = {
            "exec_kpis": kpi.get_executive_kpis(),
            "monthly": kpi.get_monthly_metrics(),
            "category": kpi.get_category_performance(),
            "channel": kpi.get_channel_performance(),
            "store": kpi.get_store_performance(),
            "segments": kpi.get_customer_segment_insights(),
            "stock_alerts": kpi.get_stockout_alerts(limit=15),
            "top_slow": kpi.get_top_selling_and_slow_moving_products(limit=10),
        }
        row_counts = {name: len(df) for name, df in kpi.get_raw_dataframes().items()}
        truth = build_ground_truth(
            data["exec_kpis"],
            {k: v for k, v in data.items() if k != "exec_kpis"},
            row_counts,
        )
        metric_keys = list(truth["kpis"].keys()) + list(truth["derived"].keys())

        agents = create_agents(llm)
        tasks = create_tasks(agents, metric_keys)
        tracker = ExecutionTracker(db, session_id, agents)

        def step_cb(step):  # records which tools each agent actually called
            tool = getattr(step, "tool", None)
            if tool:
                tracker.record_tool(str(tool), str(getattr(step, "tool_input", "")))

        # ---- Phase 1: sequential crew with shared context --------------------
        def make_callback(idx: int):
            key = ANALYSIS_KEYS[idx]

            def _cb(output):
                tracker.complete(key, getattr(output, "raw", str(output)), _snapshot(key, data))
                if idx + 1 < len(ANALYSIS_KEYS):
                    tracker.start(ANALYSIS_KEYS[idx + 1])
            return _cb

        for i, t in enumerate(tasks):
            t.callback = make_callback(i)

        crew = Crew(
            agents=[agents[k] for k in ANALYSIS_KEYS],
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
            max_rpm=CREW_MAX_RPM,
            step_callback=step_cb,
        )
        tracker.start(ANALYSIS_KEYS[0])
        result = crew.kickoff()
        raw_outputs = [o.raw for o in result.tasks_output]
        reports = dict(zip(ANALYSIS_KEYS, raw_outputs))
        plan = extract_json(reports["strategy_agent"])

        def revise_strategy(issues: List[str]) -> Optional[dict]:
            tracker.current = "strategy_agent"
            raw = _run_single(
                agents["strategy_agent"],
                create_strategy_revision_task(
                    agents["strategy_agent"],
                    {k: reports[k] for k in DESCRIPTIVE_KEYS}, issues, metric_keys),
                step_cb,
            )
            return extract_json(raw)

        if plan is None:  # one retry if the JSON was malformed
            plan = revise_strategy(["Your output was not a single valid JSON object."])
        if plan is None:
            raise ValueError("Strategy Agent did not return valid JSON after a retry.")

        # ---- Phases 2-3: deterministic audit + correction loop ---------------
        tracker.start("verification_agent")
        corrections: List[dict] = []
        audit: Dict[str, Any] = {}
        recs: List[dict] = []
        rec_checks: List[dict] = []
        for round_no in range(MAX_CORRECTION_ROUNDS + 1):
            audit = audit_reports({k: reports[k] for k in DESCRIPTIVE_KEYS}, truth)
            recs = _normalise_recommendations(plan)
            rec_checks = [validate_recommendation(r, truth) for r in recs]
            bad = [i for i, c in enumerate(rec_checks) if not c["all_valid"]]
            # Any unverifiable figure sends the report back to its author; the
            # accuracy threshold is the final approval gate, not the retry trigger.
            if audit["unverified_count"] == 0 and not bad:
                break
            if round_no == MAX_CORRECTION_ROUNDS:
                break

            issues: List[str] = []
            if audit["unverified_count"] > 0:
                by_agent: Dict[str, List[dict]] = {}
                for c in audit["unverified_claims"]:
                    by_agent.setdefault(c["agent"], []).append(c)
                for key, claims in by_agent.items():
                    tracker.current = key
                    reports[key] = _run_single(
                        agents[key],
                        create_correction_task(agents[key], reports[key], claims),
                        step_cb,
                    )
                    note = {"round": round_no + 1, "unverified_numbers_sent_back": len(claims)}
                    corrections.append({"agent": key, **note})
                    tracker.revise(key, reports[key], note)
                    issues.append(f"{_META[key][0]} report was corrected ({len(claims)} unverified numbers).")
            for i in bad:
                issues.append(f"Recommendation '{recs[i]['title']}' has missing or incorrect evidence_metrics.")
            new_plan = revise_strategy(issues)
            if new_plan is not None:
                plan = new_plan
                tracker.revise("strategy_agent", _format_strategy_text(plan),
                               {"round": round_no + 1, "reason": issues})

        # Recommendations whose evidence still fails are withheld from approval.
        valid_recs = [r for r, c in zip(recs, rec_checks) if c["all_valid"]]
        valid_checks = [c for c in rec_checks if c["all_valid"]]
        blocked = [(r, c) for r, c in zip(recs, rec_checks) if not c["all_valid"]]
        plan["recommendations"] = valid_recs

        # ---- Phase 4: Verification Agent (LLM) --------------------------------
        tracker.current = "verification_agent"
        audit_summary = {
            "accuracy_pct": audit["accuracy_pct"],
            "claims_checked": audit["claims_checked"],
            "unverified_count": audit["unverified_count"],
            "per_agent": audit["per_agent"],
            "unverified_claims": [
                {"agent": c["agent"], "claim": c["claim"], "sentence": c["context"]}
                for c in audit["unverified_claims"][:15]
            ],
            "correction_rounds": len({c["round"] for c in corrections}),
            "recommendations_withheld_for_bad_evidence": [r["title"] for r, _ in blocked],
        }
        raw_verdict = _run_single(
            agents["verification_agent"],
            create_verification_task(agents["verification_agent"],
                                     json.dumps(plan, indent=2)[:14000], audit_summary),
            step_cb,
        )
        verdict = extract_json(raw_verdict) or {}
        agent_verdict = str(verdict.get("verdict", "REJECTED")).upper()  # fail closed
        approved = (
            agent_verdict == "APPROVED"
            and audit["accuracy_pct"] >= MIN_AUDIT_ACCURACY
            and len(valid_recs) >= 1
        )

        audited = audit["unverified_claims"][:15] + audit["verified_claims"]
        scorecard = {
            "audit_timestamp": datetime.utcnow().isoformat(),
            "mathematical_accuracy_pct": audit["accuracy_pct"],
            "accuracy_threshold_pct": MIN_AUDIT_ACCURACY,
            "claims_checked": audit["claims_checked"],
            "verified_claims": audit["verified_count"],
            "hallucination_count": audit["unverified_count"],
            "per_agent": audit["per_agent"],
            "correction_rounds": len({c["round"] for c in corrections}),
            "agent_corrections": len(corrections),
            "corrections": corrections,
            "agent_verdict": agent_verdict,
            "agent_confidence": verdict.get("confidence", "Low"),
            "agent_rationale": verdict.get("rationale", "Verification Agent returned no valid JSON."),
            "unsupported_claims": verdict.get("unsupported_claims", []),
            "contradictions": verdict.get("contradictions", []),
            "low_confidence_findings": verdict.get("low_confidence_findings", []),
            "consistency_rating": "HIGH" if not verdict.get("contradictions") else "LOW",
            "audited_claims": [
                {"claim": f"{c['claim']} ({_META[c['agent']][0]})",
                 "ground_truth": c["ground_truth"], "match": c["match"]}
                for c in audited[:25]
            ],
            "recommendation_evidence": [
                {"title": r["title"], **c} for r, c in zip(valid_recs, valid_checks)
            ],
            "blocked_recommendations": [r["title"] for r, _ in blocked],
            "unverified_claims_remaining": [
                {"agent": _META[c["agent"]][0], "claim": c["claim"], "sentence": c["context"]}
                for c in audit["unverified_claims"][:15]
            ],
            "recommendation_risk_assessment": (
                f"{len(valid_recs)} recommendation(s) passed evidence checks; "
                f"{len(blocked)} withheld."
            ),
            "final_verdict": "APPROVED" if approved else "REJECTED",
        }
        verification_text = _format_verification_text(scorecard)
        tracker.complete("verification_agent", verification_text, scorecard)

        strategy_text = _format_strategy_text(plan)
        # keep the readable plan (not raw JSON) in the Strategy agent's log
        strategy_log = tracker.logs["strategy_agent"]
        strategy_log.output_text = strategy_text
        strategy_log.structured_data = {**(strategy_log.structured_data or {}),
                                        "plan": plan}
        db.commit()

        # ---- Phase 5: human-in-the-loop ----------------------------------------
        created: List[StrategicRecommendation] = []
        for r, c in [(r, c) for r, c in zip(valid_recs, valid_checks)] + blocked:
            is_valid = c["all_valid"]
            rec = StrategicRecommendation(
                session_id=session_id,
                title=r["title"],
                category=r["category"],
                description=r["description"],
                expected_roi=r["expected_roi"],
                risk_level=r["risk_level"],
                supporting_evidence=c,  # database values, not LLM claims
                status="Pending" if (approved and is_valid) else "Blocked",
            )
            db.add(rec)
            db.commit()
            db.refresh(rec)
            if approved and is_valid:  # only verified items reach a manager
                db.add(ApprovalRequest(recommendation_id=rec.id,
                                       requested_by_agent="Strategy Agent",
                                       decision="Pending"))
                db.commit()
            created.append(rec)

        # ---- Finalise session ---------------------------------------------------
        session.status = "Verified" if approved else "Completed"
        session.is_verified = approved
        session.completed_at = datetime.utcnow()
        session.execution_duration_sec = round(time.time() - t_start, 2)
        session.executive_summary = str(plan.get("executive_summary", strategy_text))
        session.verification_scorecard = scorecard
        session.consolidated_plan = {
            "executive_summary": session.executive_summary,
            "agent_results": {**reports, "strategy_agent": strategy_text,
                              "verification_agent": verification_text},
            "growth_opportunities": plan.get("growth_opportunities", []),
            "business_risks": plan.get("business_risks", []),
            "improvement_plan": plan.get("improvement_plan", []),
            "contradictions_resolved": plan.get("contradictions_resolved", []),
            "kpi_snapshot": data["exec_kpis"],
            "monthly_trends": data["monthly"],
            "category_performance": data["category"],
            "channel_performance": data["channel"],
            "recommendations": [
                {"id": r.id, "title": r.title, "category": r.category,
                 "expected_roi": r.expected_roi, "status": r.status} for r in created
            ],
        }
        db.commit()

        # ---- PDF report -----------------------------------------------------------
        pdf_path = PDFReportService().generate_consolidated_bi_report(
            session_id=session_id,
            kpi_data=data["exec_kpis"],
            monthly_data=data["monthly"],
            category_data=data["category"],
            channel_data=data["channel"],
            store_data=data["store"],
            stockout_data=data["stock_alerts"],
            strategy_text=strategy_text,
            verification_text=verification_text,
            strategy_plan=plan,
            scorecard=scorecard,
        )
        db.add(GeneratedReport(
            session_id=session_id,
            user_id=session.user_id,
            report_type="Consolidated",
            title=f"Retail Business Intelligence Report – Session #{session_id}",
            file_path=pdf_path,
            file_size_bytes=os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 0,
            period_start=datetime(2026, 5, 1).date(),
            period_end=datetime(2026, 10, 31).date(),
        ))
        db.commit()
        print(f"Session {session_id}: {session.status} in {session.execution_duration_sec}s")

    except Exception as exc:  # noqa: BLE001 - surfaced to the UI via session/log state
        db.rollback()
        message = f"{type(exc).__name__}: {exc}"
        print(f"Error in multi-agent session {session_id}: {message}")
        if tracker:
            tracker.fail_running(message)
        if session:
            session.status = "Failed"
            session.completed_at = datetime.utcnow()
            session.consolidated_plan = {"error": message[:1000]}
            db.commit()
    finally:
        db.close()
