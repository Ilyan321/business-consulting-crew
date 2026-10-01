import os
import time
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

# ─────────────────────────────────────────────────────────────
# 1. Page Configuration & Styling
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ApexConsult AI | Autonomous Business Advisory",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* Modern consulting aesthetic */
    .consult-badge {
        display: inline-block;
        padding: 4px 12px;
        background: linear-gradient(135deg, #2563EB, #1D4ED8);
        color: white;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        border-radius: 9999px;
        margin-bottom: 8px;
    }
    .consult-subhead {
        color: #475569;
        font-size: 1.05rem;
        margin-bottom: 24px;
    }
    .agent-card {
        border: 1px solid #E2E8F0;
        background-color: #F8FAFC;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
    .agent-card b {
        color: #1E293B;
    }
    .stDownloadButton button {
        background-color: #2563EB !important;
        color: white !important;
        border: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────
# 2. Preset Business Templates
# ─────────────────────────────────────────────────────────────
PRESET_TEMPLATES = {
    "Custom / Blank": {
        "idea": "",
        "industry": "",
        "market": "",
        "stage": "Seed Stage ($500K - $1.5M)",
        "focus": "",
    },
    "B2B AI Regulatory Compliance SaaS": {
        "idea": (
            "An AI-powered automated regulatory compliance and audit-readiness platform "
            "for mid-market fintech and healthcare firms. Ingests legal documents, "
            "vendor contracts, and internal policies to continuously detect compliance "
            "gaps against SOC2, HIPAA, and GDPR."
        ),
        "industry": "Enterprise Software / RegTech & LegalTech",
        "market": "North America & European Union (Mid-Market B2B)",
        "stage": "Seed Stage ($1M Seed Raised)",
        "focus": (
            "Pricing model (usage-based vs seat-based), enterprise sales cycle acceleration, "
            "defensibility against big tech, and unit economics."
        ),
    },
    "Sustainable Circular DTC Apparel": {
        "idea": (
            "A closed-loop direct-to-consumer athletic apparel brand manufactured strictly "
            "from 100% ocean-bound recycled polymers, featuring a prepaid buy-back trade-in program "
            "where worn garments are shredded and remanufactured."
        ),
        "industry": "Sustainable Consumer Goods / Apparel & Retail",
        "market": "Urban Millennials & Gen-Z (US & UK)",
        "stage": "Early Revenue / Pre-Seed ($300K Angel Investment)",
        "focus": (
            "Customer acquisition cost (CAC) reduction in privacy-first iOS era, supply chain reverse-logistics "
            "margin viability, and customer lifetime value (LTV)."
        ),
    },
    "Autonomous Drone Delivery for Diagnostics": {
        "idea": (
            "On-demand autonomous medical drone transport delivering critical pathology samples, "
            "rare blood units, and anti-venom to rural clinics and community hospitals within a 75-mile radius."
        ),
        "industry": "Healthcare Logistics & Autonomous Aviation",
        "market": "Rural US & Emerging Regional Healthcare Networks",
        "stage": "Series A ($5M Target)",
        "focus": (
            "FAA regulatory certification pathways, hospital network procurement hurdles, "
            "fleet maintenance CapEx, and break-even unit economics per flight."
        ),
    },
}

# Initialize session state variables
if "business_idea" not in st.session_state:
    st.session_state["business_idea"] = PRESET_TEMPLATES["B2B AI Regulatory Compliance SaaS"]["idea"]
if "target_industry" not in st.session_state:
    st.session_state["target_industry"] = PRESET_TEMPLATES["B2B AI Regulatory Compliance SaaS"]["industry"]
if "target_market" not in st.session_state:
    st.session_state["target_market"] = PRESET_TEMPLATES["B2B AI Regulatory Compliance SaaS"]["market"]
if "budget_or_stage" not in st.session_state:
    st.session_state["budget_or_stage"] = PRESET_TEMPLATES["B2B AI Regulatory Compliance SaaS"]["stage"]
if "strategic_focus" not in st.session_state:
    st.session_state["strategic_focus"] = PRESET_TEMPLATES["B2B AI Regulatory Compliance SaaS"]["focus"]
if "report_results" not in st.session_state:
    st.session_state["report_results"] = None

# ─────────────────────────────────────────────────────────────
# 3. Sidebar - Environment, Models & Credentials
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Advisory System Config")

    # API Key Handling (Streamlit Secrets vs Manual Input)
    detected_secret_key = get_groq_api_key()
    has_secret = bool(detected_secret_key)

    if has_secret:
        st.success("✅ Groq API Key loaded from Secrets", icon="🔑")
        use_manual_key = st.toggle("Override with custom API Key", value=False)
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
        st.warning("⚠️ No Groq API Key found in secrets", icon="⚠️")
        groq_key_input = st.text_input(
            "Enter Groq API Key",
            type="password",
            placeholder="gsk_...",
            help="Get your free key from https://console.groq.com/keys",
        )
        active_groq_key = groq_key_input.strip()

    st.divider()

    # Model Selection
    st.markdown("#### 🧠 Inference Engine (Groq)")
    selected_model_option = st.selectbox(
        "Groq Model",
        options=AVAILABLE_MODELS + ["Custom Model ID..."],
        index=0,  # Default to openai/gpt-oss-120b
        help="Model executed on Groq LPU inference engine via OpenAI-compatible endpoint.",
    )

    if selected_model_option == "Custom Model ID...":
        custom_model = st.text_input("Enter Model ID", value="openai/gpt-oss-120b")
        active_model = custom_model.strip()
    else:
        active_model = selected_model_option

    temperature = st.slider(
        "Sampling Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.05,
        help="Lower values yield more structured analytical rigor; higher values increase strategic creativity.",
    )

    # Base URL display
    st.caption(f"**Endpoint:** `{GROQ_BASE_URL}`")

    # API Connection Verification
    if st.button("🔌 Test Groq Connection", use_container_width=True):
        if not active_groq_key:
            st.error("Please enter a valid Groq API Key first.")
        else:
            with st.spinner("Testing Groq endpoint..."):
                test_result = test_groq_connection(
                    api_key=active_groq_key,
                    model=active_model,
                )
                if test_result.get("success"):
                    st.success(f"Connection OK ({test_result['latency']}s) via `{test_result.get('method')}`")
                    st.info(f"Response: {test_result.get('message')}")
                else:
                    st.error(f"Connection failed: {test_result.get('error')}")

    st.divider()

    # Multi-Agent Roster
    st.markdown("#### 👥 Multi-Agent Roster (4 Agents)")
    st.markdown(
        """
        <div class="agent-card">
            <b>1. Market Intelligence Specialist</b><br>
            <small>Macro trends, TAM/SAM/SOM, and competitive gap discovery.</small>
        </div>
        <div class="agent-card">
            <b>2. Business & Growth Strategist</b><br>
            <small>Value proposition, monetization models, and defensible moats.</small>
        </div>
        <div class="agent-card">
            <b>3. Financial & Risk Analyst</b><br>
            <small>Unit economics, cost structures, burn rate, and risk matrix.</small>
        </div>
        <div class="agent-card">
            <b>4. Executive Reviewer & Managing Partner</b><br>
            <small>Quality critique, synthesis, and 30-60-90 day execution roadmap.</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()
    st.caption("Framework: **CrewAI** | Engine: **Groq LPU** | UI: **Streamlit Cloud**")


# ─────────────────────────────────────────────────────────────
# 4. Main Panel - Header & Engagement Brief
# ─────────────────────────────────────────────────────────────
st.markdown('<div class="consult-badge">Multi-Agent Strategy Engine</div>', unsafe_allow_html=True)
st.title("💼 ApexConsult AI: Strategic Advisory Crew")
st.markdown(
    '<div class="consult-subhead">Autonomous 4-agent consulting squad collaborating via CrewAI & ultra-fast Groq inference '
    'to research, analyze, stress-test, and synthesize comprehensive C-suite business strategy reports.</div>',
    unsafe_allow_html=True,
)

# Preset Selection Bar
st.markdown("##### 📁 Load Strategic Case Study / Template")
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
        "Select a pre-filled business scenario or start blank:",
        options=list(PRESET_TEMPLATES.keys()),
        index=1,
        key="selected_template",
        on_change=on_template_change,
        label_visibility="collapsed",
    )

# Input Form
with st.container(border=True):
    st.markdown("### 📝 Business Proposal & Engagement Brief")

    business_idea_input = st.text_area(
        "Business Concept / Problem Statement *",
        value=st.session_state["business_idea"],
        placeholder="Describe the product/service, core target customer, and fundamental problem you solve...",
        height=120,
        help="Be as clear and specific as possible. The agents will build their entire strategic analysis around this.",
    )

    col1, col2 = st.columns(2)
    with col1:
        target_industry_input = st.text_input(
            "Target Industry / Domain *",
            value=st.session_state["target_industry"],
            placeholder="e.g. HealthTech, B2B SaaS, CleanTech, Logistics",
        )
        target_market_input = st.text_input(
            "Target Geography / Customer Tier",
            value=st.session_state["target_market"],
            placeholder="e.g. North America Enterprise, Global Tier-2 SMBs",
        )

    with col2:
        budget_stage_input = st.selectbox(
            "Current Stage & Capital Horizon",
            options=[
                "Idea / Concept Stage (Pre-Funding)",
                "Pre-Seed ($100K - $500K)",
                "Seed Stage ($500K - $2M)",
                "Series A ($2M - $10M)",
                "Established SME / Corporate Innovation",
            ],
            index=2,
        )
        strategic_focus_input = st.text_input(
            "Key Strategic Questions or Priorities",
            value=st.session_state["strategic_focus"],
            placeholder="e.g. Defensible moats, pricing strategy, customer acquisition bottleneck",
        )

    launch_button = st.button("🚀 Deploy Consulting Crew & Generate Advisory Report", type="primary", use_container_width=True)


# ─────────────────────────────────────────────────────────────
# 5. Engagement Execution & Multi-Agent Orchestration
# ─────────────────────────────────────────────────────────────
if launch_button:
    # Validation
    if not active_groq_key:
        st.error(
            "❌ **Groq API Key Required**: Please enter your Groq API Key in the left sidebar "
            "or configure `GROQ_API_KEY` in Streamlit Cloud Secrets (`.streamlit/secrets.toml`).",
            icon="🚨",
        )
        st.stop()

    if not business_idea_input.strip() or not target_industry_input.strip():
        st.error("❌ Please provide both a **Business Concept** and a **Target Industry** to proceed.")
        st.stop()

    # Progress and Status Container
    st.divider()
    st.markdown("### 🔄 Multi-Agent Deliberation in Progress")

    status_container = st.status("Initializing Consulting Crew...", expanded=True)

    with status_container:
        st.write("🔧 Setting up Groq inference client and assigning agent roles...")
        time.sleep(0.5)

        start_time = time.time()
        try:
            status_container.update(
                label="Executing Phase 1: Market Intelligence & Industry Deep-Dive...",
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
            )

            elapsed_total = round(time.time() - start_time, 2)
            results["elapsed_time"] = elapsed_total
            results["model"] = active_model

            st.session_state["report_results"] = results

            status_container.update(
                label=f"✅ Engagement Complete! Generated in {elapsed_total}s",
                state="complete",
                expanded=False,
            )
            st.success(f"🎉 Advisory Report successfully compiled in **{elapsed_total} seconds** using `{active_model}`!")

        except Exception as e:
            status_container.update(
                label="❌ Error occurred during agent deliberation",
                state="error",
                expanded=True,
            )
            st.error(f"**Execution Error:** {str(e)}")
            st.info(
                "💡 **Troubleshooting Tips:**\n"
                "- Verify your Groq API Key has active quota at [console.groq.com](https://console.groq.com).\n"
                "- Try selecting an alternate model such as `openai/llama-3.3-70b-versatile` in the sidebar if rate-limited."
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
    st.markdown("### 📑 Strategic Advisory Deliverables")

    # Action Toolbar: Download options
    download_col1, download_col2, metric_col1, metric_col2 = st.columns([2, 2, 1.5, 1.5])

    with download_col1:
        st.download_button(
            label="📥 Download Full Boardroom Report (.md)",
            data=final_report,
            file_name=f"strategic_advisory_report_{int(time.time())}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with download_col2:
        # Build consolidated dossier containing all agent outputs
        full_dossier = (
            f"# COMPREHENSIVE BUSINESS STRATEGY ADVISORY DOSSIER\n"
            f"**Business Proposal:** {inputs_meta.get('business_idea')}\n"
            f"**Industry:** {inputs_meta.get('target_industry')} | **Stage:** {inputs_meta.get('budget_or_stage')}\n"
            f"**Model:** {model_name} | **Generation Time:** {elapsed}s\n\n"
            f"{'='*80}\n\n"
            f"# EXECUTIVE BOARDROOM ADVISORY REPORT\n\n{final_report}\n\n"
            f"{'='*80}\n\n"
        )
        for s in step_outputs:
            full_dossier += f"## {s['title']} ({s['agent_role']})\n\n{s['content']}\n\n{'-'*60}\n\n"

        st.download_button(
            label="📁 Download Complete Consulting Dossier (.txt)",
            data=full_dossier,
            file_name=f"full_consulting_dossier_{int(time.time())}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with metric_col1:
        st.metric(label="Inference Latency", value=f"{elapsed}s")

    with metric_col2:
        tokens_info = results.get("token_usage")
        total_tokens = tokens_info.get("total_tokens", "N/A") if isinstance(tokens_info, dict) else "N/A"
        st.metric(label="Total Tokens", value=total_tokens)

    st.write("")

    # Tabbed Interface for In-Depth Exploration
    tabs = st.tabs([
        "🏆 Executive Boardroom Report",
        "🔍 Market Intelligence (Agent 1)",
        "💡 Business Strategy & GTM (Agent 2)",
        "📊 Financials & Risk Matrix (Agent 3)",
        "📋 Full Advisory Dossier",
    ])

    # Tab 1: Executive Boardroom Report
    with tabs[0]:
        st.markdown(final_report)

    # Tab 2: Market Intelligence (Agent 1)
    with tabs[1]:
        if len(step_outputs) > 0:
            st.markdown(f"### {step_outputs[0]['title']}")
            st.caption(f"**Lead Analyst:** {step_outputs[0]['agent_role']}")
            st.markdown(step_outputs[0]["content"])
        else:
            st.info("Market intelligence details are synthesized inside the main executive report.")

    # Tab 3: Business Strategy & GTM (Agent 2)
    with tabs[2]:
        if len(step_outputs) > 1:
            st.markdown(f"### {step_outputs[1]['title']}")
            st.caption(f"**Lead Analyst:** {step_outputs[1]['agent_role']}")
            st.markdown(step_outputs[1]["content"])
        else:
            st.info("Strategy formulation details are synthesized inside the main executive report.")

    # Tab 4: Financials & Risk Matrix (Agent 3)
    with tabs[3]:
        if len(step_outputs) > 2:
            st.markdown(f"### {step_outputs[2]['title']}")
            st.caption(f"**Lead Analyst:** {step_outputs[2]['agent_role']}")
            st.markdown(step_outputs[2]["content"])
        else:
            st.info("Financial stress-test details are synthesized inside the main executive report.")

    # Tab 5: Full Dossier
    with tabs[4]:
        st.markdown("### Complete Consulting Process & Agent Logs")
        for s in step_outputs:
            with st.expander(f"{s['title']} — {s['agent_role']}", expanded=False):
                st.markdown(s["content"])
