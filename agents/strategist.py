from crewai import Agent, LLM


def create_strategist_agent(llm: LLM, verbose: bool = True) -> Agent:
    """
    Agent 2: Principal Business & Growth Strategist
    Responsible for formulating core business strategy, value propositions,
    business model architecture, monetization strategies, and go-to-market roadmaps.
    """
    return Agent(
        role="Principal Business & Growth Strategist",
        goal=(
            "Formulate a defensible commercial strategy, pricing architecture, and go-to-market playbook "
            "for {business_idea}, derived directly from verified market research findings."
        ),
        backstory=(
            "You are a Senior Strategy Partner specializing in corporate development and commercial architecture. "
            "You write with razor-sharp business logic, concrete monetization models, and specific channel economics. "
            "You never speak in vague platitudes or generic marketing slogans; every strategic recommendation must be defensible and clear."
        ),
        llm=llm,
        max_iter=1,
        verbose=verbose,
        allow_delegation=False,
    )
