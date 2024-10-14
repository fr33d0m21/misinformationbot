import os
from typing import List
import asyncio
from openai import OpenAI
from swarm import Swarm, Agent 
from swarm.types import Result # Import Result from swarm.types

# Imports for handoff functions (no agent imports)
from agents.cognitive_reasoning_agent import cognitive_reasoning_handoff
from agents.claim_decomposition_agent import decomposition_handoff

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Clarification Agent ---
def rephrase_claim(claim: str) -> str:
    """Rephrases the user's claim for clarity and neutrality, 
    removing emotional charge and leading language. 
    """
    print("Rephrasing claim:", claim)
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Rephrase this claim clearly and neutrally, focusing on the core issue: "},
            {"role": "user", "content": claim}
        ],
        temperature=0.3
    )
    rephrased_claim = response.choices[0].message.content.strip()
    print("Rephrased Claim:", rephrased_claim)
    return rephrased_claim

def generate_perspectives(claim: str) -> List[str]:
    """Generates multiple perspectives on the claim 
    to encourage a balanced analysis.
    """
    print("Generating perspectives for claim:", claim)
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Provide 3 distinct perspectives on this claim, considering different viewpoints and potential biases: "},
            {"role": "user", "content": claim}
        ],
        temperature=0.7
    )
    perspectives_text = response.choices[0].message.content.strip()
    perspectives = [line.strip() for line in perspectives_text.split("\n") if line.strip()]
    print("Perspectives:", perspectives)
    return perspectives

def clarification_handoff(claim: str) -> Result:  # Add websocket parameter!
    """Handoff function to pass the rephrased claim and perspectives 
    to the Cognitive Reasoning Agent and then to the Claim Decomposition Agent
    """
    global active_websocket # Declare active_websocket as global
    rephrased = rephrase_claim(claim)
    perspectives = generate_perspectives(rephrased)
    intermediate_result = cognitive_reasoning_handoff(rephrased, perspectives) # Pass websocket 
    chain_of_thought = intermediate_result.context_variables.get("chain_of_thought")
    asyncio.run(active_websocket.send_json({
        "type": "agent_update",
        "agent": clarification_agent.name,
        "content": f"## Chain of Thought:\n\n{chain_of_thought}"
    }))
    return decomposition_handoff(chain_of_thought)  # Pass websocket

# Define the agent at the bottom of the file
clarification_agent = Agent(
    name='Clarification Agent',
    instructions='Rephrase the user claim for clarity and generate multiple perspectives for analysis.',
    functions=[rephrase_claim, generate_perspectives, clarification_handoff]
)