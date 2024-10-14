import os
from typing import Dict, Any, List

from openai import OpenAI
from swarm import Swarm, Agent 
from swarm.types import Result # Import Result from swarm.types

from agents.drafter_agent import drafter_agent, drafting_handoff
from agents.objectivity_agent import objectivity_agent, objectivity_handoff # Import for the next handoff

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Argumentation Mining Agent ---
def mine_arguments(
    rephrased_claim: str, analysis: str, research_data: Dict[str, Any]
) -> str:
    """Mines and analyzes arguments for and against the claim from the research data.
    Identifies premises and conclusions, evaluates evidence quality, and
    detects potential biases and logical fallacies.
    """
    print("Mining Arguments")
    # Format the research data for a clear presentation to the LLM
    formatted_research = ""
    for question, results in research_data.items():
        formatted_research += f"## {question}\n"
        for i, result in enumerate(results):
            source = result.get("source", "Unknown Source")
            title = result.get("title", "No Title")
            url = result.get("url", "No URL")
            snippet = result.get("snippet", "")
            formatted_research += (
                f"**Result {i+1} ({source}):**\n"
                f"   - **Title:** {title}\n"
                f"   - **URL:** {url}\n"
                f"   - **Snippet:** {snippet}\n\n"
            )

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """Identify and analyze arguments for and against the claim based on the
                              research data and analysis. Focus on:
                              - Identifying Premises and Conclusions of each argument
                              - Evaluating the quality and relevance of evidence
                              - Identifying logical fallacies and flaws in reasoning
                              - Detecting potential biases in sources or arguments""",
            },
            {
                "role": "user",
                "content": f"Claim: {rephrased_claim}\nAnalysis: {analysis}\nResearch Data: {formatted_research}",
            },
        ],
        temperature=0.3,
    )
    argumentation_analysis = response.choices[0].message.content.strip()
    print("Argumentation Analysis:", argumentation_analysis)
    return argumentation_analysis

def argumentation_handoff(rephrased_claim: str, analysis: str, research_data: Dict[str, Any]) -> Result:
    """Handoff function to pass the argument analysis to the Drafter Agent.
    """
    argumentation_analysis = mine_arguments(rephrased_claim, analysis, research_data)
    intermediate_result = drafting_handoff(argumentation_analysis)
    draft_report = intermediate_result.context_variables.get("draft_report")
    return objectivity_handoff(draft_report)

# Define the agent at the bottom of the file
argumentation_mining_agent = Agent(
    name="Argumentation Mining Agent",
    instructions="Identify and analyze arguments from the research data.",
    functions=[mine_arguments, argumentation_handoff],
)