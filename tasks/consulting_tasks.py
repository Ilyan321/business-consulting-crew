from typing import List, Callable, Optional
from crewai import Task, Agent


def create_consulting_tasks(
    researcher: Agent,
    strategist: Agent,
    financial_analyst: Agent,
    reviewer: Agent,
    task_callback: Optional[Callable] = None,
) -> List[Task]:
    """
    Creates the sequential 4-stage business consulting workflow.
    Each task builds on previous outputs and passes context downstream.
    """

    # Anti-slop quality directive applied across all consulting tasks
    anti_slop_directive = (
        "\n\nTONE & RIGOR DIRECTIVE:\n"
        "- Write strictly in the concise, objective tone of a tier-1 strategy partner.\n"
        "- Zero conversational preambles, meta-commentary, or generic AI buzzword filler.\n"
        "- Provide concrete numbers, specific named companies, explicit pricing tiers, and defensible rationale."
    )

    # Task 1: Market Research & Industry Intelligence
    market_research_task = Task(
        description=(
            "Conduct a focused market intelligence analysis for the following business proposal:\n"
            "- Business Idea: {business_idea}\n"
            "- Target Industry: {target_industry}\n"
            "- Target Market / Region: {target_market}\n"
            "- Budget / Business Stage: {budget_or_stage}\n"
            "- Strategic Focus / Key Inquiries: {strategic_focus}\n\n"
            "Provide a data-dense analysis covering:\n"
            "1. Macro Industry Dynamics & PESTLE drivers.\n"
            "2. Market Sizing Estimates: Calculated TAM, SAM, and SOM figures with assumptions.\n"
            "3. Top 3 Direct & Indirect Competitors with strengths and structural vulnerabilities.\n"
            "4. Target Customer Persona & Critical Unmet Pain Points.\n"
            "5. Strategic Market Gaps (Why now?)."
            + anti_slop_directive
        ),
        expected_output=(
            "A structured, concise Market Intelligence Dossier in Markdown with headers: "
            "### 1. Macro Industry Dynamics\n"
            "### 2. Market Sizing (TAM/SAM/SOM)\n"
            "### 3. Competitor Benchmark\n"
            "### 4. Target Customer Persona\n"
            "### 5. Strategic Market Gaps"
        ),
        agent=researcher,
        callback=task_callback,
    )

    # Task 2: Business & Growth Strategy Formulation
    strategy_formulation_task = Task(
        description=(
            "Using the Market Intelligence Dossier, design a high-impact "
            "commercial strategy and business architecture for {business_idea}.\n\n"
            "Formulate with precision:\n"
            "1. Core Value Proposition & Distinct Positioning Statement.\n"
            "2. Business Model Architecture: Specific pricing tiers, monetization mechanics, and margin structure.\n"
            "3. Defensible Competitive Moats (Network effects, switching costs, proprietary data flywheel).\n"
            "4. Go-to-Market (GTM) Playbook: Specific acquisition channels, CAC benchmarks, and key partnerships.\n"
            "5. Strategic Differentiation Matrix."
            + anti_slop_directive
        ),
        expected_output=(
            "A structured Strategic Business Blueprint in Markdown with headers: "
            "### 1. Value Proposition & Positioning\n"
            "### 2. Business Model & Monetization Architecture\n"
            "### 3. Defensible Competitive Moats\n"
            "### 4. Multi-Channel Go-To-Market Playbook\n"
            "### 5. Strategic Differentiation"
        ),
        agent=strategist,
        context=[market_research_task],
        callback=task_callback,
    )

    # Task 3: Financial Feasibility, Unit Economics & Risk Assessment
    financial_risk_task = Task(
        description=(
            "Evaluate financial viability, unit economics, cost structures, and risk factors for {business_idea} "
            "at stage: {budget_or_stage}, building directly upon the Strategy Blueprint.\n\n"
            "Quantify concisely:\n"
            "1. Unit Economics: Estimated CAC, LTV, LTV/CAC ratio, payback months, and gross margins.\n"
            "2. Cost Structure & Capital Allocation: Major CapEx requirements, monthly OpEx burn, and runway horizon.\n"
            "3. Break-Even Horizon & Revenue Milestones.\n"
            "4. Risk Matrix (High/Med/Low impact): Market, Operational, Financial, and Regulatory risks with mitigation protocols."
            + anti_slop_directive
        ),
        expected_output=(
            "A structured Financial Feasibility & Risk Audit in Markdown with headers: "
            "### 1. Unit Economics & Margin Profile\n"
            "### 2. Cost Structure & Runway Allocation\n"
            "### 3. Break-Even Projections\n"
            "### 4. Risk & Mitigation Matrix"
        ),
        agent=financial_analyst,
        context=[strategy_formulation_task],
        callback=task_callback,
    )

    # Task 4: Executive Review, Quality Audit & Boardroom Advisory Report
    executive_review_task = Task(
        description=(
            "As Senior Executive Reviewer & Managing Partner, synthesize all analyses into a complete, authoritative, "
            "and boardroom-ready Strategic Advisory Report for {business_idea}.\n\n"
            "You MUST write out and fully conclude all 5 sections from beginning to end without cutting off:\n"
            "# 1. Executive Summary & Strategic Viability Scorecard\n"
            "# 2. Strategic Value Architecture & Go-to-Market Highlights\n"
            "# 3. Financial Viability, Unit Economics (CAC/LTV) & Capital Requirements\n"
            "# 4. Critical Vulnerabilities & Risk Mitigation Matrix\n"
            "# 5. Phased 30-60-90 Day Actionable Execution Roadmap & Final Verdict"
            + anti_slop_directive
        ),
        expected_output=(
            "A complete, fully finished Boardroom Strategic Advisory Report in clean Markdown with all 5 numbered sections "
            "fully written out, concluding with the concrete 30-60-90 day roadmap and final investment verdict."
        ),
        agent=reviewer,
        context=[market_research_task, strategy_formulation_task, financial_risk_task],
        callback=task_callback,
    )

    return [
        market_research_task,
        strategy_formulation_task,
        financial_risk_task,
        executive_review_task,
    ]
