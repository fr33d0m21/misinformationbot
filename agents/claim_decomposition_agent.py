import os
from typing import List

from openai import OpenAI
from swarm import Swarm, Agent 
from swarm.types import Result # Import Result from swarm.types

# Import handoff function (no agent import)
from agents.question_generation_agent import question_generation_handoff

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Claim Decomposition Agent ---
def decompose_claim(chain_of_thought: str) -> List[str]:
    """Decomposes the claim into smaller, verifiable sub-claims 
    that are specific, measurable, achievable, relevant, and time-bound (SMART). 
    """
    print("Decomposing Claim...")
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Decompose this claim into 5 SMART sub-claims that can be researched independently, considering this chain of thought: "},
            {"role": "user", "content": f"Chain of Thought: {chain_of_thought}"}
        ],
        temperature=0.5
    )
    subclaims_text = response.choices[0].message.content.strip()
    subclaims = [line.strip() for line in subclaims_text.split("\n") if line.strip()]
    print("Subclaims:", subclaims)
    return subclaims

def decomposition_handoff(chain_of_thought: str) -> Result:
    """Handoff function to pass the sub-claims to the 
    Question Generation Agent.
    """
    subclaims = decompose_claim(chain_of_thought)
    return question_generation_handoff(subclaims, chain_of_thought)

claim_decomposition_agent = Agent(
    name='Claim Decomposition Agent',
    instructions='Decompose the claim into smaller, verifiable SMART sub-claims.',
    functions=[decompose_claim, decomposition_handoff]
)