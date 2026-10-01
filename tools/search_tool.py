from typing import Optional
from crewai.tools import tool
from duckduckgo_search import DDGS


@tool("DuckDuckGo Web Search")
def duckduckgo_web_search(query: str) -> str:
    """
    Search the live web using DuckDuckGo to obtain up-to-date market intelligence,
    real competitor profiles, recent industry reports, and live market statistics.
    Input should be a targeted search query string.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=2))
            if not results:
                return f"No live web search results found for query: '{query}'."

            formatted_results = []
            for item in results:
                title = item.get("title", "Untitled")
                link = item.get("href", "")
                snippet = item.get("body", "")[:180]
                formatted_results.append(
                    f"- **{title}**: {snippet} ({link})"
                )

            return "\n".join(formatted_results)
    except Exception as e:
        return f"Web search notice: {str(e)}"
