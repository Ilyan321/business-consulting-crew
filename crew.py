import _compat  # noqa: F401
from typing import Dict, Any, Optional, Callable, Tuple, List
from crewai import Crew, Process, LLM

from config import get_llm, DEFAULT_MODEL
from agents import (
    create_researcher_agent,
    create_strategist_agent,
    create_financial_analyst_agent,
    create_reviewer_agent,
)
from tasks import create_consulting_tasks
from tools import duckduckgo_web_search


def build_consulting_crew(
    llm: LLM,
    task_callback: Optional[Callable] = None,
    enable_web_search: bool = True,
    verbose: bool = True,
) -> Tuple[Crew, Dict[str, Any]]:
    """
    Assembles the 4 specialized agents and their sequential tasks into
    a unified CrewAI multi-agent consulting pipeline.
    """
    # 1. Prepare tools
    researcher_tools = [duckduckgo_web_search] if enable_web_search else []

    # 2. Instantiate the specialized agents
    researcher = create_researcher_agent(llm=llm, tools=researcher_tools, verbose=verbose)
    strategist = create_strategist_agent(llm=llm, verbose=verbose)
    financial_analyst = create_financial_analyst_agent(llm=llm, verbose=verbose)
    reviewer = create_reviewer_agent(llm=llm, verbose=verbose)

    agents_dict = {
        "researcher": researcher,
        "strategist": strategist,
        "financial_analyst": financial_analyst,
        "reviewer": reviewer,
    }

    # 3. Instantiate the interconnected sequential tasks
    tasks = create_consulting_tasks(
        researcher=researcher,
        strategist=strategist,
        financial_analyst=financial_analyst,
        reviewer=reviewer,
        task_callback=task_callback,
    )

    # 4. Assemble the Crew
    consulting_crew = Crew(
        agents=[researcher, strategist, financial_analyst, reviewer],
        tasks=tasks,
        process=Process.sequential,
        verbose=verbose,
    )

    return consulting_crew, agents_dict


def run_consulting_pipeline(
    business_idea: str,
    target_industry: str,
    target_market: str = "Global / North America",
    budget_or_stage: str = "Early Stage / Seed ($250k - $1M)",
    strategic_focus: str = "Market expansion, defensibility, and unit economics",
    api_key: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    enable_web_search: bool = True,
    task_callback: Optional[Callable] = None,
) -> Dict[str, Any]:
    """
    Executes the full consulting pipeline from end-to-end.
    Returns the final report, individual task artifacts, and usage metrics.
    """
    # Initialize the Groq LLM
    llm = get_llm(api_key=api_key, model=model, temperature=temperature)

    # Assemble the crew with optional live web search tool
    crew, agents = build_consulting_crew(
        llm=llm,
        task_callback=task_callback,
        enable_web_search=enable_web_search,
    )

    # Prepare inputs dictionary
    inputs = {
        "business_idea": business_idea.strip(),
        "target_industry": target_industry.strip(),
        "target_market": target_market.strip(),
        "budget_or_stage": budget_or_stage.strip(),
        "strategic_focus": strategic_focus.strip(),
    }

    # Execute crew kickoff
    crew_output = crew.kickoff(inputs=inputs)

    # Parse individual task outputs
    step_outputs = []
    task_titles = [
        "1. Market & Competitive Intelligence",
        "2. Strategic Business Architecture & GTM",
        "3. Financial Feasibility & Risk Audit",
        "4. Executive Boardroom Advisory Report",
    ]

    if hasattr(crew_output, "tasks_output") and crew_output.tasks_output:
        for idx, task_out in enumerate(crew_output.tasks_output):
            title = task_titles[idx] if idx < len(task_titles) else f"Step {idx+1}"
            step_outputs.append({
                "step_index": idx + 1,
                "title": title,
                "agent_role": getattr(task_out, "agent", "Consultant"),
                "content": getattr(task_out, "raw", str(task_out)),
                "summary": getattr(task_out, "summary", ""),
            })

    return {
        "final_report": getattr(crew_output, "raw", str(crew_output)),
        "step_outputs": step_outputs,
        "token_usage": getattr(crew_output, "token_usage", None),
        "inputs": inputs,
    }
