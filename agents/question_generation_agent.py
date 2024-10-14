import os
from typing import List
import asyncio
import websockets
from openai import OpenAI
from swarm import Swarm, Agent 
from swarm.types import Result # Import Result from swarm.types

# Import handoff function
from agents.research_agent import research_handoff

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Maximum number of Tavily searches allowed
MAX_TAVILY_SEARCHES = 25

# --- Question Generation Agent ---
def generate_questions(subclaims: List[str], chain_of_thought: str) -> List[str]:
    """Generates insightful research questions for each sub-claim,
    prioritizing questions that can be answered through research using
    publicly available information and data. Questions are limited to
    between 4 and 400 characters to comply with Tavily's requirements.
    """
    print("Generating Research Questions...")
    research_questions = []
    for i, subclaim in enumerate(subclaims):
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": f"""Generate 3 research questions for sub-claim {i+1} that are between 4 
                                  and 400 characters long and can be answered using publicly available 
                                  information. Consider this chain of thought: """,
                },
                {
                    "role": "user",
                    "content": f"Sub-claim: {subclaim}\nChain of Thought: {chain_of_thought}",
                },
            ],
            temperature=0.5,
        )
        questions_text = response.choices[0].message.content.strip()
        questions = [line.strip() for line in questions_text.split("\n") if line.strip()]
        research_questions.extend(questions)

    # Limit the number of research questions for Tavily
    research_questions = research_questions[:MAX_TAVILY_SEARCHES] 
    
    print("Research Questions:", research_questions)
    return research_questions

def question_generation_handoff(subclaims: List[str], chain_of_thought: str) -> Result:
    """Handoff function to pass the research questions
    to the Research Agent.
    """
    global active_websocket # Declare active_websocket as global
    research_questions = generate_questions(subclaims, chain_of_thought)
    # Send agent_update message 
    asyncio.run(active_websocket.send_json({
        "type": "agent_update",
        "agent": question_generation_agent.name,
        "content": f"## Research Questions:\n\n{research_questions}"
    }))
    return research_handoff(research_questions)

question_generation_agent = Agent(
    name="Question Generation Agent",
    instructions="Generate insightful research questions based on the sub-claims.",
    functions=[generate_questions, question_generation_handoff],
)