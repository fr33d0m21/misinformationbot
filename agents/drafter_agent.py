import os
from typing import Dict, Any, List
import asyncio
from openai import OpenAI
from swarm import Swarm, Agent 
from swarm.types import Result # Import Result from swarm.types
import websockets


# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# --- Drafter Agent ---
def draft_report(
    claim: str,
    rephrased_claim: str,
    chain_of_thought: str,
    subclaims: List[str],
    research_questions: List[str],
    research_data: Dict[str, Any],
    analysis: str,
    argumentation_analysis: str,
) -> str:
    """Generates a comprehensive report summarizing the truth analysis process and findings.
    Includes sections for the claim, clarification, chain of thought, research questions,
    research findings, argumentation analysis, overall analysis, and a conclusion.
    """
    print("Drafting Report...")
    # Format the data for a clear presentation to the LLM
    formatted_research = ""
    for question, results in research_data.items():
        formatted_research += f"### {question}\n"
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

    formatted_subclaims = "\n".join([f"- {sc}" for sc in subclaims])
    formatted_questions = "\n".join([f"- {rq}" for rq in research_questions])

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """Generate a detailed and well-structured report summarizing the truth
                              analysis process.  Use the following sections:
                              - **Claim:** The original claim.
                              - **Clarified Claim:** The rephrased claim.
                              - **Chain of Thought:** The reasoning steps used in the analysis.
                              - **Sub-claims:** The decomposed sub-claims.
                              - **Research Questions:** The questions generated for research.
                              - **Research Findings:** A summary of the research data.
                              - **Argumentation Analysis:** Analysis of arguments for and against the claim.
                              - **Overall Analysis:** An assessment of the claim's truthfulness.
                              - **Conclusion:**  A concise summary of the findings.

                              Ensure the report is unbiased, written in clear language, and well-organized.
                              Do not include any information about your cutoff date or that you are an AI agent.""",
            },
            {
                "role": "user",
                "content": f"Original Claim: {claim}\nClarified Claim: {rephrased_claim}\nChain of Thought: {chain_of_thought}\nSub-claims: {formatted_subclaims}\nResearch Questions: {formatted_questions}\nResearch Findings: {formatted_research}\nArgumentation Analysis: {argumentation_analysis}\nOverall Analysis: {analysis}",
            },
        ],
        temperature=0.3,
    )
    draft_report = response.choices[0].message.content.strip()
    print("Draft Report:", draft_report)
    return draft_report

def drafting_handoff(draft_report: str) -> Result:
    """Handoff function to pass the draft report to the Objectivity Agent.
    """
    global active_websocket # Declare active_websocket as global
    # Send agent_update message 
    asyncio.run(active_websocket.send_json({
        "type": "agent_update",
        "agent": drafter_agent.name,
        "content": f"## Draft Report:\n\n{draft_report}"
    }))
    return Result(
        value="Completed drafting the report.",
        context_variables={"draft_report": draft_report},
    )

# Define the agent at the bottom of the file
drafter_agent = Agent(
    name="Drafter Agent",
    instructions="Draft a comprehensive report summarizing the truth analysis.",
    functions=[draft_report, drafting_handoff],
)