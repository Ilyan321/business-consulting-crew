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
            "Conduct exhaustive market, industry, and competitor intelligence "
            "for {business_idea} within the {target_industry} sector. Identify market drivers, "
            "TAM/SAM/SOM growth potential, customer segments, and direct/indirect competitors."
        ),
        backstory=(
            "You are a seasoned Principal Market Intelligence Specialist with over 15 years "
            "of experience leading strategy intelligence units at top-tier research institutes "
            "and management consultancies. You possess unmatched expertise in PESTLE analysis, "
            "Porter's Five Forces, consumer segment profiling, and identifying market white-spaces. "
            "You utilize real-time search tools to ground your insights in actual live market data."
        ),
        llm=llm,
        tools=tools or [],
        verbose=verbose,
        allow_delegation=False,
    )
