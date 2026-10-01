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

    # Task 1: Market Research & Industry Intelligence
    market_research_task = Task(
        description=(
            "Conduct an in-depth market intelligence investigation for the following business proposal:\n"
            "- Business Idea: {business_idea}\n"
            "- Target Industry: {target_industry}\n"
            "- Target Market / Region: {target_market}\n"
            "- Budget / Business Stage: {budget_or_stage}\n"
            "- Strategic Focus / Key Inquiries: {strategic_focus}\n\n"
            "Your analysis must address:\n"
            "1. Macro Industry Trends: Key market drivers, technological tailwinds, regulatory shifts (PESTLE).\n"
            "2. Market Sizing: Realistic breakdown of Total Addressable Market (TAM), Serviceable Available Market (SAM), "
            "and Serviceable Obtainable Market (SOM).\n"
            "3. Competitive Landscape: Direct and indirect competitors, their market share, core strengths, and structural weaknesses.\n"
            "4. Customer Personas & Pain Points: Primary and secondary buyer personas, critical unmet needs, and purchasing triggers.\n"
            "5. Strategic Market Gaps: Under-served market niches and timing advantages (Why Now?)."
        ),
        expected_output=(
            "A structured Market Intelligence Dossier formatted in Markdown with clear section headers: "
            "Macro Industry Dynamics, TAM/SAM/SOM Market Sizing, Competitor Benchmark Matrix, "
            "Customer Persona Deep Dive, and Strategic Market Gaps."
        ),
        agent=researcher,
        callback=task_callback,
    )

    # Task 2: Business & Growth Strategy Formulation
    strategy_formulation_task = Task(
        description=(
            "Using the Market Intelligence Dossier from the Researcher, design a comprehensive, defensible "
            "business strategy and commercial architecture for {business_idea}.\n\n"
            "Your strategic plan must formulate:\n"
            "1. Core Value Proposition: Distinctive positioning statement and unique selling proposition (USP).\n"
            "2. Business Model Architecture: Revenue streams, pricing tiers, monetization mechanics, and margin structure.\n"
            "3. Competitive Moat & Flywheel: Long-term defensibility factors (network effects, switching costs, proprietary tech/data, brand).\n"
            "4. Go-to-Market (GTM) Strategy: Optimal customer acquisition channels, partnership opportunities, and viral/referral loops.\n"
            "5. Strategic Positioning: Perceptual positioning against key competitors identified in the research phase."
        ),
        expected_output=(
            "A structured Strategic Business Blueprint formatted in Markdown with sections: "
            "Executive Value Proposition, Business Model & Monetization Architecture, "
            "Defensible Competitive Moats, Multi-Channel Go-To-Market Playbook, and Strategic Positioning Map."
        ),
        agent=strategist,
        context=[market_research_task],
        callback=task_callback,
    )

    # Task 3: Financial Feasibility, Unit Economics & Risk Assessment
    financial_risk_task = Task(
        description=(
            "Evaluate the financial viability, unit economics, cost structures, and risk exposure of {business_idea} "
            "given the budget/stage: {budget_or_stage}, based on the Market Dossier and Strategic Blueprint.\n\n"
            "Your financial and risk analysis must calculate/estimate:\n"
            "1. Unit Economics: Estimated Customer Acquisition Cost (CAC), Lifetime Value (LTV), LTV/CAC ratio, and gross margins.\n"
            "2. Cost Structure & Capital Allocation: Major CapEx requirements, OpEx drivers (engineering, marketing, G&A), and runway assumptions.\n"
            "3. Break-Even & Revenue Milestones: Realistic horizon to cash flow positivity and sensitivity to conversion rates.\n"
            "4. Operational & Regulatory Vulnerabilities: Key supply chain, staffing, compliance, or tech stack dependencies.\n"
            "5. Comprehensive Risk Mitigation Matrix: Categorize risks (High/Medium/Low impact & probability) covering "
            "Market Risk, Financial Risk, Execution Risk, and Regulatory Risk, accompanied by proactive mitigation protocols."
        ),
        expected_output=(
            "A structured Financial Feasibility & Risk Audit formatted in Markdown with sections: "
            "Unit Economics & Margin Profile, Cost Structure Breakdown, Break-Even Projections, "
            "and a Comprehensive Risk & Mitigation Matrix."
        ),
        agent=financial_analyst,
        context=[market_research_task, strategy_formulation_task],
        callback=task_callback,
    )

    # Task 4: Executive Review, Quality Audit & Boardroom Advisory Report
    executive_review_task = Task(
        description=(
            "As Senior Executive Reviewer & Managing Partner, audit, critique, harmonize, and synthesize the outputs "
            "from Market Research, Business Strategy, and Financial Risk into a single, cohesive, boardroom-ready "
            "Business Strategy Advisory Report for {business_idea}.\n\n"
            "Your responsibilities:\n"
            "1. Audit & Reconcile: Eliminate conflicting assumptions between market projections, strategic claims, and unit economics.\n"
            "2. Executive Critique: Highlight critical vulnerabilities, unaddressed blind spots, or over-optimistic projections.\n"
            "3. Executive Summary: Deliver a crisp, 1-page executive summary with a Strategic Viability Scorecard (Rating: High / Moderate / Conditional).\n"
            "4. Phased 30-60-90 Day Execution Roadmap: Concrete, sequential milestones and KPIs for immediate post-launch execution.\n"
            "5. Final Strategic Advisory Recommendation: Unambiguous Go/Pivot/No-Go verdict with key conditions for success."
        ),
        expected_output=(
            "An authoritative Boardroom-Ready Business Strategy Advisory Report in clean Markdown, containing:\n"
            "# 1. Executive Summary & Strategic Viability Scorecard\n"
            "# 2. Consolidated Market Intelligence & Strategic Architecture\n"
            "# 3. Financial Viability, Unit Economics & Key Assumptions\n"
            "# 4. Executive Critical Audit & Risk Mitigation Protocols\n"
            "# 5. Phased 30-60-90 Day Actionable Implementation Roadmap\n"
            "# 6. Final Advisory Verdict & Resource Allocation Guidance"
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
