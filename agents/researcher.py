from typing import Optional, List, Any
from crewai import Agent, LLM


def create_researcher_agent(
    llm: LLM,
    tools: Optional[List[Any]] = None,
    verbose: bool = True,
) -> Agent:
    """
    Agent 1: Market & Industry Research Specialist
    Responsible for industry macroeconomic trends, competitive benchmarking,
    TAM/SAM/SOM market sizing, and consumer demand dynamics.
    Can utilize live web search tools to fetch current market intelligence.
    """
    return Agent(
        role="Senior Market & Competitive Intelligence Specialist",
        goal=(
            "Conduct exhaustive, data-grounded market intelligence for {business_idea} in {target_industry}. "
            "Identify precise TAM/SAM/SOM market sizing, named competitors, structural market gaps, and customer friction points."
        ),
        backstory=(
            "You are a seasoned Market Intelligence Director formerly leading strategy think tanks at top-tier management consultancies. "
            "You write in a crisp, data-dense, executive tone. You despise generic AI clichés, fluff, and superficial generalities. "
            "You provide concrete estimates, named market players, and factual market dynamics with zero throat-clearing or filler."
        ),
        llm=llm,
        tools=tools or [],
        max_iter=2,
        verbose=verbose,
        allow_delegation=False,
    )
