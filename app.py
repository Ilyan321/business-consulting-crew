import _compat  # noqa: F401 - Apply Python 3.14+ Pydantic v1 patch before CrewAI imports
import os
import time
import json
import streamlit as st
from typing import Dict, Any

from config import (
    DEFAULT_MODEL,
    AVAILABLE_MODELS,
    GROQ_BASE_URL,
    get_groq_api_key,
    test_groq_connection,
)
from crew import run_consulting_pipeline
from db_supabase import (
    is_supabase_configured,
    save_report_to_supabase,
    fetch_reports_from_supabase,
)

# ─────────────────────────────────────────────────────────────
# 1. Page Configuration & Styling
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Apex Strategic Advisory | Executive Diligence Platform",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* Institutional corporate strategy aesthetic */
    .consult-badge {
        display: inline-block;
        padding: 4px 12px;
        background-color: #0F172A;
        color: #F8FAFC;
        font-size: 0.76rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        border-radius: 4px;
        margin-bottom: 8px;
    }
    .consult-subhead {
        color: #334155;
        font-size: 1.02rem;
        line-height: 1.55;
        margin-bottom: 24px;
    }
    .agent-card {
        border: 1px solid #E2E8F0;
        background-color: #F8FAFC;
        border-radius: 6px;
        padding: 10px 14px;
        margin-bottom: 8px;
    }
    .agent-card b {
        color: #0F172A;
        font-size: 0.88rem;
    }
    .agent-card small {
        color: #475569;
        font-size: 0.78rem;
    }
    .stDownloadButton button {
        background-color: #0F172A !important;
        color: #FFFFFF !important;
        border: 1px solid #0F172A !important;
        border-radius: 6px !important;
    }
    .stDownloadButton button:hover {
        background-color: #1E293B !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────
# 2. Preset Business Templates (Pakistan & Emerging Markets + Global)
# ─────────────────────────────────────────────────────────────
PRESET_TEMPLATES = {
    "Custom / Blank": {
        "idea": "",
        "industry": "",
        "market": "",
        "stage": "Seed Stage ($100K - $500K)",
        "focus": "",
    },
    "🇵🇰 Pakistan: Kiryana & SME Micro-Lending Platform (Fintech)": {
        "idea": (
            "An AI-driven micro-lending and automated credit-scoring platform for informal kiryana (retail grocery) stores and small merchants across Pakistan. "
            "Ingests digital ledger transactions, Raast, JazzCash, and supplier invoicing data to underwrite collateral-free 30-day working capital loans."
        ),
        "industry": "Fintech / SME Digital Credit & Embedded Finance",
        "market": "Pakistan (Karachi, Lahore, Faisalabad, Rawalpindi & Tier-2 Commercial Hubs)",
        "stage": "Seed Stage (PKR 50M - 150M / $200K - $500K)",
        "focus": (
            "State Bank of Pakistan (SBP) digital lending regulatory compliance, default rate mitigation in informal cash retail, "
            "and distribution partnership with FMCG distributors (Unilever, Nestlé)."
        ),
    },
    "🇵🇰 Pakistan: Direct Farm-to-Retail AgriTech Supply Chain (AgriTech)": {
        "idea": (
            "A B2B farm-to-retail procurement marketplace connecting smallholder wheat, rice, citrus, and vegetable farmers in Sindh & Punjab directly "
            "with urban supermarkets, restaurants, and wholesale mandees, eliminating exploitative middlemen (arthis) and deploying cold-storage transit."
        ),
        "industry": "AgriTech & Cold-Chain Perishable Logistics",
        "market": "Rural Sindh/Punjab ➔ Urban Metros (Karachi, Lahore, Islamabad)",
        "stage": "Seed Stage ($500K - $1.5M)",
        "focus": (
            "Farmer seasonal working capital advances, post-harvest spoilage reduction (cold logistics), "
            "and wholesale price transparency algorithms."
        ),
    },
    "🇵🇰 Pakistan: Rooftop Solar Leasing & IoT Net-Metering (CleanTech)": {
        "idea": (
            "Zero-down distributed rooftop solar power-purchase-agreement (PPA) leasing and smart IoT net-metering for textile factories, "
            "commercial plazas, and residential housing societies battling soaring NEPRA/DISCO electricity tariffs and grid load-shedding."
        ),
        "industry": "Renewable Energy / Distributed Commercial Solar",
        "market": "Pakistan Industrial Clusters (Karachi, Sialkot, Faisalabad, Gujranwala)",
        "stage": "Series A ($2M - $5M)",
        "focus": (
            "Import currency FX devaluation hedging on solar inverters/panels, DISCO grid-tie regulatory bottlenecks, "
            "and long-term commercial PPA payment enforcement."
        ),
    },
    "🇵🇰 Pakistan: US & GCC Remote Tech Talent Cloud (B2B Services)": {
        "idea": (
            "A curated talent marketplace connecting vetted Pakistani full-stack software engineers, AI researchers, and DevOps specialists "
            "directly with tech startups and enterprises in Silicon Valley, London, Riyadh, and Dubai, with automated escrow payments and local compliance."
        ),
        "industry": "B2B Tech Services & Cross-Border Engineering Cloud",
        "market": "Pakistani Software Engineers ➔ US, UK & GCC Enterprise Clients (Riyadh, Dubai, US)",
        "stage": "Early Revenue / Pre-Seed ($150K - $300K)",
        "focus": (
            "US/GCC enterprise client acquisition, senior engineer retention against international remote jobs, "
            "and gross margin optimization on monthly billable hours."
        ),
    },
    "🌍 Global: B2B Enterprise Compliance & Audit SaaS": {
        "idea": (
            "An enterprise compliance automation platform for mid-market fintech and healthcare firms. "
            "Ingests vendor contracts and internal policies to continuously detect compliance gaps across SOC 2, HIPAA, and GDPR."
        ),
        "industry": "Enterprise Software / RegTech & LegalTech",
        "market": "North America & European Union (Mid-Market B2B)",
        "stage": "Seed Stage ($1M Raised)",
        "focus": (
            "Usage-based vs seat-based pricing architecture, enterprise sales cycle compression, "
            "and defensibility against legacy GRC vendors."
        ),
    },
}

# Initialize session state variables
DEFAULT_PRESET_KEY = "🇵🇰 Pakistan: Kiryana & SME Micro-Lending Platform (Fintech)"

if "business_idea" not in st.session_state:
    st.session_state["business_idea"] = PRESET_TEMPLATES[DEFAULT_PRESET_KEY]["idea"]
if "target_industry" not in st.session_state:
    st.session_state["target_industry"] = PRESET_TEMPLATES[DEFAULT_PRESET_KEY]["industry"]
if "target_market" not in st.session_state:
    st.session_state["target_market"] = PRESET_TEMPLATES[DEFAULT_PRESET_KEY]["market"]
if "budget_or_stage" not in st.session_state:
    st.session_state["budget_or_stage"] = PRESET_TEMPLATES[DEFAULT_PRESET_KEY]["stage"]
if "strategic_focus" not in st.session_state:
    st.session_state["strategic_focus"] = PRESET_TEMPLATES[DEFAULT_PRESET_KEY]["focus"]
if "report_results" not in st.session_state:
    st.session_state["report_results"] = None

# ─────────────────────────────────────────────────────────────
# 3. Sidebar - Environment, Models, Web Tools & Supabase
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### System Configuration")

    # API Key Handling
    detected_secret_key = get_groq_api_key()
    has_secret = bool(detected_secret_key)

    if has_secret:
        st.success("API Key Active (Streamlit Secrets)")
        use_manual_key = st.toggle("Override API Key", value=False)
        if use_manual_key:
            groq_key_input = st.text_input(
                "Custom Groq API Key",
                type="password",
                placeholder="gsk_...",
                help="Enter a Groq API key to override the environment key.",
            )
            active_groq_key = groq_key_input.strip() if groq_key_input else detected_secret_key
        else:
            active_groq_key = detected_secret_key
    else:
        st.warning("No Groq API Key found in secrets")
        groq_key_input = st.text_input(
            "Enter Groq API Key",
            type="password",
            placeholder="gsk_...",
            help="Get your key from https://console.groq.com/keys",
        )
        active_groq_key = groq_key_input.strip()

    st.divider()

    # Model Selection
    st.markdown("#### Inference Engine")
    selected_model_option = st.selectbox(
        "Model ID",
        options=AVAILABLE_MODELS + ["Custom Model ID..."],
        index=0,
        help="gpt-oss-20b delivers high speed and high token throughput. gpt-oss-120b provides deep-tier reasoning.",
    )

    if selected_model_option == "Custom Model ID...":
        custom_model = st.text_input("Model Name", value="openai/gpt-oss-20b")
        active_model = custom_model.strip()
    else:
        active_model = selected_model_option

    temperature = st.slider(
        "Analytical Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.05,
        help="Lower values enforce structured analytical precision; higher values increase strategic divergence.",
    )

    # Web Search Tool Toggle
    st.markdown("#### Real-Time Intelligence")
    enable_web_search = st.toggle(
        "Live Market Data (DuckDuckGo)",
        value=True,
        help="Enables live web queries for up-to-date competitor intelligence and market statistics.",
    )

    # Supabase Cloud Storage Status
    st.markdown("#### Cloud Repository")
    if is_supabase_configured():
        st.success("Supabase Active (Cloud Archive Connected)")
    else:
        st.caption("Supabase: Optional (Running in Session Mode)")

    # API Connection Verification
    if st.button("Test Endpoint Connection", use_container_width=True):
        if not active_groq_key:
            st.error("Please enter a valid Groq API Key first.")
        else:
            with st.spinner("Pinging endpoint..."):
                test_result = test_groq_connection(
                    api_key=active_groq_key,
                    model=active_model,
                )
                if test_result.get("success"):
                    st.success(f"Connection Verified ({test_result['latency']}s latency)")
                else:
                    st.error(f"Connection failed: {test_result.get('error')}")

    st.divider()

    # Multi-Agent Roster
    st.markdown("#### Specialized Advisory Council")
    st.markdown(
        """
        <div class="agent-card">
            <b>1. Market Intelligence Director</b><br>
            <small>TAM/SAM/SOM sizing, PESTLE dynamics, competitor benchmarking.</small>
        </div>
        <div class="agent-card">
            <b>2. Commercial & Growth Strategist</b><br>
            <small>Monetization architecture, pricing tiers, defensible moats.</small>
        </div>
        <div class="agent-card">
            <b>3. Quantitative Financial Analyst</b><br>
            <small>CAC/LTV unit economics, CapEx/OpEx burn, 4-tier risk matrix.</small>
        </div>
        <div class="agent-card">
            <b>4. Executive Review Partner</b><br>
            <small>Audit reconciliation, strategic scorecard, 30-60-90 day plan.</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()
    st.caption("Engine: **CrewAI + Groq LPU** | Data: **DuckDuckGo** | Storage: **Supabase**")


# ─────────────────────────────────────────────────────────────
# 4. Main Panel - Header & Engagement Brief
# ─────────────────────────────────────────────────────────────
st.markdown('<div class="consult-badge">Institutional Diligence Platform</div>', unsafe_allow_html=True)
st.title("Apex Strategic Advisory")
st.markdown(
    '<div class="consult-subhead">Autonomous corporate strategy, commercial diligence, and risk governance system. '
    'Coordinates market intelligence, commercial architecture, quantitative unit economics, and executive review into boardroom-ready deliverables.</div>',
    unsafe_allow_html=True,
)

# Preset Selection Bar
st.markdown("##### Load Strategic Case Profile")
template_col, clear_col = st.columns([4, 1])

with template_col:
    def on_template_change():
        chosen = st.session_state["selected_template"]
        if chosen in PRESET_TEMPLATES:
            data = PRESET_TEMPLATES[chosen]
            st.session_state["business_idea"] = data["idea"]
            st.session_state["target_industry"] = data["industry"]
            st.session_state["target_market"] = data["market"]
            st.session_state["budget_or_stage"] = data["stage"]
            st.session_state["strategic_focus"] = data["focus"]

    selected_template = st.selectbox(
        "Select a pre-filled scenario or start blank:",
        options=list(PRESET_TEMPLATES.keys()),
        index=1,
        key="selected_template",
        on_change=on_template_change,
        label_visibility="collapsed",
    )

# Input Form
with st.container(border=True):
    st.markdown("### Strategic Brief & Opportunity Profile")

    business_idea_input = st.text_area(
        "Commercial Concept / Core Value Proposition *",
        value=st.session_state["business_idea"],
        placeholder="Describe the product/service, core target customer, and fundamental problem addressed...",
        height=110,
        help="Be specific. The analysis derives its strategic depth directly from this brief.",
    )

    col1, col2 = st.columns(2)
    with col1:
        target_industry_input = st.text_input(
            "Industry Sector & Domain *",
            value=st.session_state["target_industry"],
            placeholder="e.g. Enterprise Software, CleanTech, Health Logistics",
        )
        target_market_input = st.text_input(
            "Target Geography & Customer Tier",
            value=st.session_state["target_market"],
            placeholder="e.g. North America Enterprise, Global Mid-Market",
        )

    with col2:
        budget_stage_input = st.selectbox(
            "Capital Horizon & Stage",
            options=[
                "Concept / Pre-Seed ($100K - $500K)",
                "Seed Stage ($500K - $2M)",
                "Series A / Growth ($2M - $10M)",
                "Enterprise Innovation / Corporate Pivot",
            ],
            index=1,
        )
        strategic_focus_input = st.text_input(
            "Priority Inquiries or Strategic Bottlenecks",
            value=st.session_state["strategic_focus"],
            placeholder="e.g. Pricing architecture, defensibility against incumbents, CAC efficiency",
        )

    launch_button = st.button("Generate Strategic Advisory Report", type="primary", use_container_width=True)


# ─────────────────────────────────────────────────────────────
# 5. Engagement Execution & Multi-Agent Orchestration
# ─────────────────────────────────────────────────────────────
if launch_button:
    # Validation
    if not active_groq_key:
        st.error(
            "**API Key Required**: Please enter your Groq API Key in the left sidebar "
            "or configure `GROQ_API_KEY` in Streamlit Cloud Secrets.",
            icon="⚠️",
        )
        st.stop()

    if not business_idea_input.strip() or not target_industry_input.strip():
        st.error("Please provide both a **Commercial Concept** and a **Target Industry** to proceed.")
        st.stop()

    # Progress and Status Container
    st.divider()
    st.markdown("### Strategic Diligence in Progress")

    status_container = st.status("Initializing Strategic Advisory Council...", expanded=True)

    with status_container:
        st.write("Configuring agent reasoning constraints and live research tools...")
        time.sleep(0.3)

        start_time = time.time()
        try:
            status_container.update(
                label="Executing 4-Phase Diligence Pipeline (Market Research ➔ Strategy ➔ Unit Economics ➔ Executive Audit)...",
                state="running",
            )

            # Run the multi-agent pipeline
            results = run_consulting_pipeline(
                business_idea=business_idea_input,
                target_industry=target_industry_input,
                target_market=target_market_input,
                budget_or_stage=budget_stage_input,
                strategic_focus=strategic_focus_input,
                api_key=active_groq_key,
                model=active_model,
                temperature=temperature,
                enable_web_search=enable_web_search,
            )

            elapsed_total = round(time.time() - start_time, 2)
            results["elapsed_time"] = elapsed_total
            results["model"] = active_model

            # Save to Supabase if configured
            if is_supabase_configured():
                st.write("Archiving deliverable to cloud repository...")
                save_report_to_supabase(
                    business_idea=business_idea_input,
                    target_industry=target_industry_input,
                    target_market=target_market_input,
                    budget_or_stage=budget_stage_input,
                    strategic_focus=strategic_focus_input,
                    final_report=results.get("final_report", ""),
                    step_outputs=results.get("step_outputs", []),
                    model=active_model,
                    elapsed_time=elapsed_total,
                )

            st.session_state["report_results"] = results

            status_container.update(
                label=f"Strategic Diligence Complete ({elapsed_total}s)",
                state="complete",
                expanded=False,
            )
            st.success(f"Advisory Report compiled in **{elapsed_total} seconds** using `{active_model}`.")

        except Exception as e:
            status_container.update(
                label="Diligence halted due to execution error",
                state="error",
                expanded=True,
            )
            st.error(f"**Execution Error:** {str(e)}")
            st.info(
                "**Troubleshooting:**\n"
                "- Verify your Groq API Key has active quota at [console.groq.com](https://console.groq.com).\n"
                "- Ensure `openai/gpt-oss-20b` is selected for optimal speed and throughput."
            )
            st.stop()


# ─────────────────────────────────────────────────────────────
# 6. Deliverable Presentation & Multi-Tab Report Explorer
# ─────────────────────────────────────────────────────────────
if st.session_state["report_results"]:
    results = st.session_state["report_results"]
    final_report = results.get("final_report", "")
    step_outputs = results.get("step_outputs", [])
    inputs_meta = results.get("inputs", {})
    elapsed = results.get("elapsed_time", 0.0)
    model_name = results.get("model", active_model)

    st.markdown("---")
    st.markdown("### Strategic Advisory Deliverables")

    # Action Toolbar: Download options
    download_col1, download_col2, metric_col1, metric_col2 = st.columns([2, 2, 1.5, 1.5])

    with download_col1:
        st.download_button(
            label="Download Executive Boardroom Report (.md)",
            data=final_report,
            file_name=f"strategic_advisory_report_{int(time.time())}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with download_col2:
        # Build consolidated dossier containing all agent outputs
        full_dossier = (
            f"# COMPREHENSIVE STRATEGIC ADVISORY DOSSIER\n"
            f"**Commercial Brief:** {inputs_meta.get('business_idea')}\n"
            f"**Industry Sector:** {inputs_meta.get('target_industry')} | **Stage:** {inputs_meta.get('budget_or_stage')}\n"
            f"**Execution Engine:** {model_name} | **Turnaround:** {elapsed}s\n\n"
            f"{'='*80}\n\n"
            f"# EXECUTIVE BOARDROOM ADVISORY REPORT\n\n{final_report}\n\n"
            f"{'='*80}\n\n"
        )
        for s in step_outputs:
            full_dossier += f"## {s['title']} ({s['agent_role']})\n\n{s['content']}\n\n{'-'*60}\n\n"

        st.download_button(
            label="Download Complete Diligence Dossier (.txt)",
            data=full_dossier,
            file_name=f"full_consulting_dossier_{int(time.time())}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with metric_col1:
        st.metric(label="Turnaround Time", value=f"{elapsed}s")

    with metric_col2:
        st.metric(label="Model Engine", value=model_name.replace("openai/", ""))

    st.write("")

    # Tabbed Interface for In-Depth Exploration
    tabs = st.tabs([
        "Executive Boardroom Report",
        "Market Intelligence Dossier",
        "Commercial Strategy & GTM",
        "Financial Model & Risk Matrix",
        "Consolidated Advisory Dossier",
        "Archived Engagements (Supabase)",
    ])

    # Tab 1: Executive Boardroom Report
    with tabs[0]:
        st.markdown(final_report)

    # Tab 2: Market Intelligence (Agent 1)
    with tabs[1]:
        if len(step_outputs) > 0:
            st.markdown(f"### {step_outputs[0]['title']}")
            st.caption(f"**Lead Director:** {step_outputs[0]['agent_role']}")
            st.markdown(step_outputs[0]["content"])
        else:
            st.info("Market intelligence details are synthesized inside the main executive report.")

    # Tab 3: Business Strategy & GTM (Agent 2)
    with tabs[2]:
        if len(step_outputs) > 1:
            st.markdown(f"### {step_outputs[1]['title']}")
            st.caption(f"**Lead Director:** {step_outputs[1]['agent_role']}")
            st.markdown(step_outputs[1]["content"])
        else:
            st.info("Commercial strategy details are synthesized inside the main executive report.")

    # Tab 4: Financials & Risk Matrix (Agent 3)
    with tabs[3]:
        if len(step_outputs) > 2:
            st.markdown(f"### {step_outputs[2]['title']}")
            st.caption(f"**Lead Director:** {step_outputs[2]['agent_role']}")
            st.markdown(step_outputs[2]["content"])
        else:
            st.info("Financial modeling details are synthesized inside the main executive report.")

    # Tab 5: Full Dossier
    with tabs[4]:
        st.markdown("### Complete Diligence Audit Trail & Agent Deliverables")
        for s in step_outputs:
            with st.expander(f"{s['title']} — {s['agent_role']}", expanded=False):
                st.markdown(s["content"])

    # Tab 6: Supabase Saved Reports
    with tabs[5]:
        st.markdown("### Historical Advisory Archives")
        if is_supabase_configured():
            saved_reports = fetch_reports_from_supabase()
            if saved_reports:
                st.write(f"Found **{len(saved_reports)}** archived advisory reports:")
                for r in saved_reports:
                    with st.expander(f"📁 {r.get('target_industry', 'Report')} — {r.get('created_at', '')[:10]} ({r.get('model_used', '')})"):
                        st.markdown(f"**Commercial Concept:** {r.get('business_idea')}")
                        st.markdown(f"**Target Market:** {r.get('target_market')} | **Stage:** {r.get('budget_or_stage')}")
                        st.divider()
                        st.markdown(r.get("final_report", ""))
            else:
                st.info("No archived reports in cloud repository yet.")
        else:
            st.info(
                "**Connect Supabase Cloud Storage:**\n\n"
                "To store and view past consulting reports permanently:\n"
                "1. Add `SUPABASE_URL` and `SUPABASE_KEY` to your Streamlit Cloud Secrets.\n"
                "2. All completed deliverables will automatically persist here."
            )
