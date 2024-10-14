import os
from typing import List
import asyncio
from openai import OpenAI
from swarm import Swarm, Agent 
from swarm.types import Result # Import Result from swarm.types
import websockets
# Import handoff function (no agent import)
from agents.claim_decomposition_agent import decomposition_handoff

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# --- Cognitive Reasoning Agent ---
def generate_chain_of_thought(rephrased_claim: str, perspectives: List[str]) -> str:
    """Generates a chain of thought incorporating deductive, inductive, 
    analogical, abductive, and causal reasoning, considering 
    different perspectives and potential biases.
    """
    print("Generating chain of thought for claim:", rephrased_claim)
    perspectives_str = "\n".join([f"- {p}" for p in perspectives])
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """Generate a detailed chain of thought for analyzing the truthfulness of this claim, 
                          considering these perspectives.  Incorporate the following reasoning methods: 
                          - Deductive Reasoning: Apply general principles to draw logical conclusions.
                          - Inductive Reasoning: Identify patterns and trends in evidence.
                          - Analogical Reasoning: Explore similar cases or analogies.
                          - Abductive Reasoning: Consider possible explanations and evaluate likelihood.
                          - Causal Reasoning: Investigate cause-and-effect relationships.
                          Do not include any information about your cutoff date or that you are an AI agent."""
            },
            {"role": "user", "content": f"Claim: {rephrased_claim}\nPerspectives: {perspectives_str}"}
        ],
        temperature=0.3
    )
    chain_of_thought = response.choices[0].message.content.strip()
    print("Chain of Thought:", chain_of_thought)
    return chain_of_thought

def cognitive_reasoning_handoff(rephrased_claim: str, perspectives: List[str]) -> Result:
    """Handoff function to pass the chain of thought 
    to the Claim Decomposition Agent.
    """
    global active_websocket # Declare active_websocket as global
    chain_of_thought = generate_chain_of_thought(rephrased_claim, perspectives)

    # Send agent_update message using await
    asyncio.run(active_websocket.send_json({
        "type": "agent_update",
        "agent": cognitive_reasoning_agent.name,
        "content": f"## Chain of Thought:\n\n{chain_of_thought}"
    }))
    return decomposition_handoff(chain_of_thought)

cognitive_reasoning_agent = Agent(
    name='Cognitive Reasoning Agent',
    instructions='Generate a detailed chain of thought incorporating various reasoning methods.',
    functions=[generate_chain_of_thought, cognitive_reasoning_handoff]
)