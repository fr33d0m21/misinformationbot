import os
import json
import uuid
import logging
from typing import List, Dict, Any

import asyncio
import redis
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from openai import OpenAI
from tavily import TavilyClient
from swarm import Swarm, Agent 
from swarm.types import Result # Import Result from swarm.types

# Import all agent modules
from agents.clarification_agent import clarification_agent, clarification_handoff
from agents.cognitive_reasoning_agent import cognitive_reasoning_agent, cognitive_reasoning_handoff
from agents.claim_decomposition_agent import claim_decomposition_agent, decomposition_handoff
from agents.question_generation_agent import question_generation_agent, question_generation_handoff
from agents.research_agent import research_agent, research_handoff
from agents.analyst_agent import analyst_agent, analyst_handoff
from agents.argumentation_mining_agent import argumentation_mining_agent, argumentation_handoff
from agents.drafter_agent import drafter_agent, drafting_handoff
from agents.objectivity_agent import objectivity_agent, objectivity_handoff
from agents.data_visualization_reporting_agent import visualization_agent, visualization_handoff
from agents.user_feedback_explanation_agent import feedback_agent, feedback_handoff
from agents.followup_agent import followup_agent, answer_followup

# Load environment variables from .env file
load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily allow all origins for debugging
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Retrieve API keys and Redis configuration from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


# Validate API keys
if not OPENAI_API_KEY:
    logger.error("Missing OPENAI_API_KEY environment variable.")
    raise EnvironmentError("Missing OPENAI_API_KEY environment variable.")
if not TAVILY_API_KEY:
    logger.error("Missing TAVILY_API_KEY environment variable.")
    raise EnvironmentError("Missing TAVILY_API_KEY environment variable.")


# Initialize Redis client
try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    redis_client.ping()
    logger.info(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
except redis.ConnectionError as e:
    logger.error(f"Could not connect to Redis: {e}")
    raise e

# Initialize OpenAI and Tavily clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
swarm_client = Swarm()

# --------------- Helper Functions ---------------
def generate_session_id():
    return str(uuid.uuid4())

def store_session_data(session_id: str, data: Dict[str, Any]) -> None:
    redis_client.set(session_id, json.dumps(data))

def get_session_data(session_id: str) -> Dict[str, Any]:
    data_json = redis_client.get(session_id)
    if data_json:
        return json.loads(data_json)
    return None

# -------------------------------------------------

# --- Misinformation Agent (Entry Point) ---
misinformation_agent = Agent(
    name="Misinformation Agent",
    instructions="You are a detective-like AI, designed to analyze the truthfulness of claims. \
                       Do not answer the claim directly. Always use the 'clarification_handoff' \
                       function to initiate the analysis process.",
    functions=[clarification_handoff],
    tool_choice="auto" 
)

# -------------------------------------------------

# ---------- WebSocket Endpoint ----------
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    logger.info(f"WebSocket connection established for session ID: {session_id}")

    try:
        while True:
            message = await websocket.receive_json()

            if message["type"] == "new_question":
                claim = message["content"]

                # Store initial claim in session data
                initial_data = {"claim": claim}
                store_session_data(session_id, initial_data)
                print("Starting Swarm workflow...")

                # Initiate the Swarm workflow
                await websocket.send_json({"type": "thinking", "content": "Analyzing..."})
                response = swarm_client.run(
                    agent=misinformation_agent,
                    messages=[{"role": "user", "content": claim}],
                    context_variables={"session_id": session_id}
                )

                print("Swarm response:", response)

                # Update the session data with the results
                session_data = get_session_data(session_id)
                session_data.update(response.context_variables)
                store_session_data(session_id, session_data)

                # Send back the final user_feedback
                await websocket.send_json({"type": "final_report", "content": response.context_variables.get('user_feedback', 'No feedback generated.')})

            elif message["type"] == "followup":
                followup_question = message["content"]
                session_data = get_session_data(session_id)

                if session_data:
                    await websocket.send_json({"type": "thinking", "content": "Thinking..."})
                    followup_answer = answer_followup(followup_question, session_data)
                    await websocket.send_json({"type": "followup_response", "content": followup_answer})
                else:
                    await websocket.send_json({"type": "error", "content": "No existing session found."})

            else:
                logger.warning("Invalid message type received: %s", message["type"])

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_json({"type": "error", "content": f"An error occurred: {str(e)}"})

    finally:
        await websocket.close()
        logger.info(f"WebSocket connection closed for session ID: {session_id}")

# -------------------------------------------------

# --------  HTML Endpoints  --------
@app.get("/", response_class=HTMLResponse)
async def read_homepage():
    with open("templates/homepage.html") as f:
        html_content = f.read()
    return html_content

@app.get("/dashboard", response_class=HTMLResponse)
async def read_dashboard():
    with open("templates/index.html") as f:
        html_content = f.read()
    return html_content

# -------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")