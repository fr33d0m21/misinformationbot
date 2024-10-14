import os
import requests
from typing import List, Dict, Any

from openai import OpenAI
from tavily import TavilyClient
from swarm import Agent
from swarm.types import Result
from agents.analyst_agent import analyst_handoff

# Initialize clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# --- Research Agent ---
def search_tavily(question: str, domains: List[str] = None) -> List[dict]:
    print(f"Searching for: {question} using the Tavily API...")
    """Searches for information using the Tavily API, focusing on
    reliable sources within specified domains.
    """
    if domains is None:
        domains = [
            "cia.gov",
            "fbi.gov",
            "state.gov",
            "congress.gov",
            "uscis.gov",
            "nasa.gov",
            "nih.gov",
            "cdc.gov",
            "epa.gov",
            "treasury.gov",
            "justice.gov",
            "defense.gov",
            "energy.gov",
            "commerce.gov",
            "labor.gov",
            "transportation.gov",
            "hud.gov",
            "education.gov",
            "va.gov",
        ]
    results = tavily_client.search(question, include_domains=domains, max_results=5)
    print("Tavily results:", results)  # Debugging print
    return results.get("results", [])

def research_handoff(research_questions: List[str]) -> Result:
    """Conducts research on each question using Tavily and hands off
    to the Analyst Agent.
    """
    print("Entering research_handoff...")  # Debug print
    research_results = {}
    for question in research_questions:
        print(f"Researching question: {question}")  # Debug print
        tavily_results = search_tavily(question)
        research_results[question] = tavily_results
    print("Research results:", research_results)  # Debug print
    rephrased_claim = "Rephrased Claim"
    chain_of_thought = "Chain of Thought"
    return analyst_handoff(rephrased_claim, chain_of_thought, research_results)


research_agent = Agent(
    name="Research Agent",
    instructions="Conduct research on the provided questions using various reliable sources.",
    functions=[search_tavily, research_handoff],
)