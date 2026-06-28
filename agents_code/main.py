from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from app.agents.icp_agent import qualify_lead
from app.config_manager import ConfigManager
from app.graph import app as agent_graph
from app.tools.memory import HAS_REDIS, get_memory_store
from app.utils.formatters import format_score, format_trigger_summary

# ---------------------------------------------------------------------------
# UI Layer — Streamlit entrypoint. State management and rendering only.
# Logic Layer (graph, agents, tools) is imported and invoked, not defined here.
# ---------------------------------------------------------------------------

load_dotenv()

st.set_page_config(page_title="Agentic AI Platform", layout="wide")
st.title("Agentic AI Platform")

# --- Initialise session state ---
if "user_id" not in st.session_state:
    st.session_state.user_id = "default"

store = get_memory_store()
config_mgr = ConfigManager(
    user_id=st.session_state.user_id,
    memory_store=store,
)
cfg = config_mgr.get_config()

# --- Sidebar: platform configuration & system status ---
with st.sidebar:
    st.header("Platform Configuration")
    side_industry = st.text_input(
        "Default Industry",
        value=cfg["icp_criteria"]["industry"],
        key="side_industry",
    )
    side_min_emp = st.number_input(
        "Default Min Employees",
        min_value=0,
        value=cfg["icp_criteria"]["min_employees"],
        key="side_min_emp",
    )
    side_personas = st.multiselect(
        "Default Personas",
        cfg["personas"]["options"],
        default=cfg["personas"]["default"],
        key="side_personas",
    )

    if st.button("Save Configuration", type="secondary", use_container_width=True):
        config_mgr.save_config({
            "icp_criteria": {
                "industry": side_industry,
                "min_employees": side_min_emp,
            },
            "personas": {
                "default": side_personas,
            },
        })
        st.success("Configuration saved!")

    st.divider()
    st.subheader("System Status")

    if store._use_redis:
        st.success("Redis: Connected")
    elif HAS_REDIS:
        st.warning("Redis: Connection refused — using in-memory fallback")
    else:
        st.info("Memory: In-Memory (redis not installed)")

    st.caption("LLM: llama-3.3-70b-versatile (Groq)")

# --- Main tabs ---
tab_analysis, tab_history = st.tabs(["Analysis", "History"])

# ---------------------------------------------------------------------------
# TAB 1: Analysis — company input, run analysis, approve/review results
# ---------------------------------------------------------------------------
with tab_analysis:
    company_url = st.text_input("Company URL", placeholder="https://example.com")
    industry = st.text_input(
        "Target Industry",
        placeholder="AI / SaaS",
        value=st.session_state.side_industry,
    )
    min_employees = st.number_input(
        "Min Employees",
        min_value=0,
        value=st.session_state.side_min_emp,
    )
    personas = st.multiselect(
        "Target Personas",
        cfg["personas"]["options"],
        default=st.session_state.side_personas,
    )
    force_refresh = st.checkbox(
        "Force re-analysis (ignore cached data)",
        value=False,
        key="force_refresh",
    )

    base_state = {
        "company_url": company_url,
        "icp_criteria": {
            "industry": industry,
            "min_employees": min_employees,
            "qualification_threshold": cfg["scoring"]["qualification_threshold"],
        },
        "raw_content": "",
        "extracted_triggers": [],
        "qualification_score": 0,
        "is_qualified": False,
        "summary": "",
        "company_name": "",
        "industry": "",
        "employee_count": 0,
        "next_actions": [],
        "contacts": [],
        "personas": personas,
        "from_memory": False,
        "human_feedback": "",
        "edited_icp": {},
        "approval_status": "pending",
        "recommended_action": {},
        "execution_plan": [],
        "current_step_index": 0,
        "prospect_intelligence": {},
        "user_id": st.session_state.user_id,
        "force_refresh": force_refresh,
        "messages": [],
        "trigger_score": 0,
        "industry_score": 0,
        "employee_score": 0,
    }

    # --- Logic Layer: first phase of graph (check_memory → extract → qualify → human_review) ---
    if st.button("Run Analysis") and company_url:
        with st.spinner("Running initial analysis..."):
            try:
                result = agent_graph.invoke(base_state)
            except Exception as e:
                st.error(f"Analysis failed: {e}")
                st.stop()
        st.session_state.pending_result = result
        st.rerun()

    pending = st.session_state.get("pending_result")
    if pending and pending.get("company_url") == company_url:
        result = pending

        col1, col2, col3 = st.columns(3)
        col1.metric("Score", format_score(result["qualification_score"]))
        col2.metric("Qualified", "Yes" if result["is_qualified"] else "No")
        col3.metric("Triggers Found", len(result["extracted_triggers"]))

        cname = result.get("company_name") or "—"
        emp = result.get("employee_count") or "?"
        st.markdown(
            f":office: **{cname}** &nbsp;·&nbsp; "
            f"👤 {emp} employees &nbsp;·&nbsp; "
            f":label: {result.get('industry') or result['icp_criteria'].get('industry', '?')}"
        )

        ts = result.get("trigger_score", 0)
        inds = result.get("industry_score", 0)
        emps = result.get("employee_score", 0)
        st.markdown(
            f":chart_with_upwards_trend: **Score Breakdown** — "
            f"Trigger: :blue[**{ts}/50**]  "
            f"Industry: :green[**{inds}/30**]  "
            f"Size: :orange[**{emps}/20**]"
        )

        with st.expander("Raw Content", expanded=False):
            st.text(result["raw_content"])

        with st.expander("Extracted Triggers", expanded=True):
            for t in result["extracted_triggers"]:
                source = t.get("source_url", "")
                with st.container(border=True):
                    st.markdown(
                        f"**{t.get('trigger_type', '?')}** "
                        f"(confidence: {t.get('confidence', 0)})"
                    )
                    st.caption(t.get("description", ""))
                    if source:
                        st.markdown(f"Source: `{source}`")

        st.divider()
        st.subheader("Approval Required")
        st.caption("Review the qualification result and choose an action.")

        # --- Logic Layer: second phase (plan → execute → aggregate → summary → save) ---
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("Approve & Enrich", type="primary", use_container_width=True):
                with st.spinner("Running enrichment..."):
                    try:
                        final = agent_graph.invoke({
                            **result,
                            "human_feedback": "approve",
                            "approval_status": "approved",
                        })
                    except Exception as e:
                        st.error(f"Enrichment failed: {e}")
                        st.stop()
                st.session_state.final_result = final
                st.session_state.pending_result = None
                st.rerun()

        with col_b:
            if st.button("Reject", type="secondary", use_container_width=True):
                with st.spinner("Saving..."):
                    try:
                        agent_graph.invoke({
                            **result,
                            "human_feedback": "reject",
                            "approval_status": "rejected",
                        })
                    except Exception as e:
                        st.error(f"Failed to save: {e}")
                        st.stop()
                st.session_state.pending_result = None
                st.rerun()

        with col_c:
            if st.button("Edit ICP", use_container_width=True):
                st.session_state.show_edit_icp = True

        if st.session_state.get("show_edit_icp"):
            with st.form(key="edit_icp_form"):
                new_industry = st.text_input(
                    "Industry",
                    value=result["icp_criteria"].get("industry", ""),
                )
                new_min_emp = st.number_input(
                    "Min Employees",
                    min_value=0,
                    value=result["icp_criteria"].get("min_employees", 0),
                )
                new_max_emp = st.number_input(
                    "Max Employees",
                    min_value=0,
                    value=result["icp_criteria"].get("max_employees", 0),
                )

                if st.form_submit_button("Apply Edited ICP"):
                    try:
                        edited_icp = {
                            "industry": new_industry,
                            "min_employees": new_min_emp,
                            "max_employees": new_max_emp,
                        }
                        updated = qualify_lead({
                            **result,
                            "icp_criteria": edited_icp,
                        })
                        result.update(updated)
                        result["edited_icp"] = edited_icp
                        result["icp_criteria"] = edited_icp
                        st.session_state.pending_result = result
                        st.session_state.show_edit_icp = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"ICP update failed: {e}")

    # --- Enrichment results (after Approve & Enrich) ---
    final = st.session_state.get("final_result")
    if final and final.get("company_url") == company_url:
        st.success("Approval completed — enrichment results below.")

        col1, col2, col3 = st.columns(3)
        col1.metric("Score", format_score(final["qualification_score"]))
        col2.metric("Qualified", "Yes" if final["is_qualified"] else "No")
        col3.metric(
            "Triggers Found",
            len(final["extracted_triggers"]),
            help=format_trigger_summary(final["extracted_triggers"]),
        )

        cname_f = final.get("company_name") or "—"
        emp_f = final.get("employee_count") or "?"
        st.markdown(
            f":office: **{cname_f}** &nbsp;·&nbsp; "
            f"👤 {emp_f} employees &nbsp;·&nbsp; "
            f":label: {final.get('industry') or final['icp_criteria'].get('industry', '?')}"
        )

        tsf = final.get("trigger_score", 0)
        indf = final.get("industry_score", 0)
        empf = final.get("employee_score", 0)
        st.markdown(
            f":chart_with_upwards_trend: **Score Breakdown** — "
            f"Trigger: :blue[**{tsf}/50**]  "
            f"Industry: :green[**{indf}/30**]  "
            f"Size: :orange[**{empf}/20**]"
        )

        execution_plan = final.get("execution_plan", [])
        if execution_plan:
            with st.expander("Execution Plan", expanded=True):
                for i, step in enumerate(execution_plan, 1):
                    st.markdown(f"{i}. **{step['tool']}** — {step['reason']}")

        pi = final.get("prospect_intelligence", {})
        if pi:
            st.subheader("Prospect Intelligence")
            cols = st.columns(3)
            with cols[0]:
                tech = pi.get("tech_stack", [])
                if tech:
                    st.markdown("**Tech Stack**")
                    tags = " ".join(f":blue-background[`{t}`]" for t in tech)
                    st.markdown(tags)
            with cols[1]:
                sentiment = pi.get("sentiment", "")
                if sentiment:
                    st.markdown("**Sentiment**")
                    icon = {"Positive": "🟢", "Negative": "🔴", "Neutral": "🟡"}
                    st.markdown(f"{icon.get(sentiment, '⚪')} {sentiment}")
            with cols[2]:
                velocity = pi.get("hiring_velocity", "")
                if velocity:
                    st.markdown("**Hiring Velocity**")
                    badge = {"High": "🔴 High", "Medium": "🟡 Medium", "Low": "🟢 Low"}
                    st.markdown(badge.get(velocity, velocity))

            insight = pi.get("strategic_insight", "")
            if insight:
                with st.container(border=True):
                    st.markdown(f"**Strategic Insight**")
                    st.markdown(insight)

        if final["is_qualified"]:
            st.subheader("Executive Brief")
            st.markdown(final["summary"])

            recommended = final.get("recommended_action")
            if recommended:
                st.subheader("Next Best Action")
                with st.container(border=True):
                    col_type, col_reason = st.columns([1, 3])
                    with col_type:
                        st.markdown(f"**{recommended.get('action_type', 'N/A')}**")
                    with col_reason:
                        st.markdown(recommended.get("reasoning", ""))

                    draft = recommended.get("draft_message", "")
                    st.code(draft, language="text")

            st.subheader("Key Contacts")
            for contact in final.get("contacts", []):
                source = contact.get("source", "")
                with st.container(border=True):
                    col_left, col_right = st.columns([1, 2])
                    with col_left:
                        st.markdown(f"**{contact['name']}**")
                        if source == "hunter":
                            st.caption(":white_check_mark: Hunter.io")
                        elif source == "limit":
                            st.caption(":warning: Search limit reached")
                        elif source == "error":
                            st.caption(":x: Error")
                    with col_right:
                        st.markdown(f"Role: {contact['role']}")
                        if contact.get("email"):
                            st.markdown(f"Email: {contact['email']}")
                        if contact.get("linkedin"):
                            st.markdown(f"LinkedIn: {contact['linkedin']}")
                        if contact.get("message"):
                            st.markdown(contact["message"])
        else:
            st.warning(
                f"Not Qualified — Score: {final['qualification_score']}/100."
            )

        if st.button("Clear Result"):
            st.session_state.final_result = None
            st.rerun()

# ---------------------------------------------------------------------------
# TAB 2: History — cached company profiles with status & date filters
# ---------------------------------------------------------------------------
with tab_history:
    store = get_memory_store()
    profiles = store.get_all_profiles()

    status_filter = st.selectbox(
        "Filter by Status",
        ["All", "Qualified", "Rejected", "Not Qualified"],
    )

    filtered = []
    for url, data in profiles.items():
        match = True
        if status_filter != "All":
            data_status = data.get("status", "")
            if status_filter == "Qualified" and data_status != "qualified":
                match = False
            elif status_filter == "Rejected" and data_status != "rejected":
                match = False
            elif status_filter == "Not Qualified" and data_status != "not_qualified":
                match = False
        if match:
            filtered.append((url, data))

    filtered.sort(
        key=lambda x: x[1].get("timestamp", ""),
        reverse=True,
    )

    if not filtered:
        st.info("No matching companies found.")
    else:
        for url, data in filtered:
            ts = data.get("timestamp", "")
            display_ts = ""
            if ts:
                try:
                    dt = datetime.fromisoformat(ts)
                    display_ts = dt.strftime("%Y-%m-%d %H:%M")
                except ValueError:
                    display_ts = ts

            status_label = data.get("status", "unknown").replace("_", " ").title()

            with st.container(border=True):
                col_a, col_b, col_c, col_d = st.columns([3, 1, 1, 1])
                with col_a:
                    st.markdown(f"**{url}**")
                    if data.get("company_name"):
                        st.caption(f"Name: {data['company_name']}")
                    if display_ts:
                        st.caption(display_ts)
                with col_b:
                    st.metric("Score", format_score(data.get("qualification_score", 0)))
                with col_c:
                    st.markdown(status_label)
                with col_d:
                    pi = data.get("prospect_intelligence", {})
                    sentiment = pi.get("sentiment", "")
                    if sentiment:
                        icon = {"Positive": "🟢", "Negative": "🔴", "Neutral": "🟡"}
                        st.markdown(icon.get(sentiment, "⚪"))

        if st.button("Clear Memory", type="secondary"):
            store.clear()
            st.rerun()
