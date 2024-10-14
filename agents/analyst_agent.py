import os
from typing import Dict, Any

from openai import OpenAI
from swarm import Swarm, Agent 
from swarm.types import Result # Import Result from swarm.types

# Import necessary for handoff
from agents.argumentation_mining_agent import argumentation_handoff

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Analyst Agent ---
def analyze_research(
    rephrased_claim: str, chain_of_thought: str, research_data: Dict[str, Any]
) -> str:
    """Analyzes the research data, considering the rephrased claim,
    chain of thought, and evidence from different sources. Identifies
    key insights, supporting/refuting evidence, potential biases, and
    inconsistencies.
    """
    print("Analyzing Research Data...")
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
                "content": """Analyze the research data to determine the truthfulness of the claim,
                              considering the chain of thought. Identify key insights, supporting or
                              refuting evidence, potential biases in sources, and any inconsistencies
                              in the information. Be thorough and present your analysis in a well-organized way.""",
            },
            {
                "role": "user",
                "content": f"Claim: {rephrased_claim}\nChain of Thought: {chain_of_thought}\nResearch Data: {formatted_research}",
            },
        ],
        temperature=0.3,
    )
    analysis = response.choices[0].message.content.strip()
    print("Analysis:", analysis)
    return analysis

def analyst_handoff(rephrased_claim: str, chain_of_thought: str, research_data: Dict[str, Any]) -> Result:
    """Handoff function to pass the analysis to the Argumentation Mining Agent.
    """
    analysis = analyze_research(rephrased_claim, chain_of_thought, research_data)
    return argumentation_handoff(rephrased_claim, analysis, research_data) 

# Define the agent at the bottom of the file
analyst_agent = Agent(
    name="Analyst Agent",
    instructions="Analyze the collected research data and assess the claim's truthfulness.",
    functions=[analyze_research, analyst_handoff],
)