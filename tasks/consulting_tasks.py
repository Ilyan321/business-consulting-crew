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
            "Conduct a focused market intelligence analysis for the following business proposal:\n"
            "- Business Idea: {business_idea}\n"
            "- Target Industry: {target_industry}\n"
            "- Target Market / Region: {target_market}\n"
            "- Budget / Business Stage: {budget_or_stage}\n"
            "- Strategic Focus / Key Inquiries: {strategic_focus}\n\n"
            "Provide a concise, high-density analysis covering:\n"
            "1. Macro Industry Dynamics & PESTLE trends.\n"
            "2. Market Sizing Estimates: Realistic TAM, SAM, and SOM figures.\n"
            "3. Top 3 Direct & Indirect Competitors with strengths and weaknesses.\n"
            "4. Target Customer Persona & Critical Unmet Pain Points.\n"
            "5. Strategic Market Gaps (Why now?)."
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
            "Using the Market Intelligence Dossier from the Researcher, design a high-impact "
            "business strategy and commercial architecture for {business_idea}.\n\n"
            "Formulate concisely:\n"
            "1. Core Value Proposition & Positioning Statement.\n"
            "2. Business Model Architecture: Pricing tiers, monetization mechanics, and revenue streams.\n"
            "3. Defensible Competitive Moats (Network effects, switching costs, proprietary technology).\n"
            "4. Go-to-Market (GTM) Playbook: Primary customer acquisition channels and partnerships.\n"
            "5. Strategic Differentiation Map."
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
            "at stage: {budget_or_stage}, building upon the Strategy Blueprint.\n\n"
            "Calculate/estimate concisely:\n"
            "1. Estimated Unit Economics: CAC, LTV, LTV/CAC ratio, and gross margin targets.\n"
            "2. Cost Structure Breakdown: CapEx requirements and monthly OpEx drivers.\n"
            "3. Break-Even Horizon & Revenue Milestones.\n"
            "4. Risk Matrix (High/Med/Low impact): Market, Operational, Financial, and Regulatory risks with mitigation protocols."
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
            "As Senior Executive Reviewer & Managing Partner, audit and synthesize the outputs "
            "from Market Research, Business Strategy, and Financial Risk into a polished, boardroom-ready "
            "Business Strategy Advisory Report for {business_idea}.\n\n"
            "Your deliverable must include:\n"
            "1. Executive Summary & Strategic Viability Scorecard (Rating: High / Moderate / Conditional).\n"
            "2. Key Strategic Takeaways & Value Architecture.\n"
            "3. Critical Vulnerabilities & Stress-Test Audit.\n"
            "4. Actionable 30-60-90 Day Post-Launch Implementation Roadmap.\n"
            "5. Final Go/Pivot/No-Go Advisory Verdict."
        ),
        expected_output=(
            "An authoritative Boardroom-Ready Business Strategy Advisory Report in clean Markdown:\n"
            "# 1. Executive Summary & Strategic Scorecard\n"
            "# 2. Strategic Value Architecture & Market Position\n"
            "# 3. Financial Viability & Critical Stress-Test Findings\n"
            "# 4. Actionable 30-60-90 Day Execution Roadmap\n"
            "# 5. Final Strategic Verdict & Next Steps"
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
