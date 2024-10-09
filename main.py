import os
import json
import logging
import uuid
from typing import Dict, Any, List, Optional

import asyncio
import redis
import tiktoken
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from openai import AsyncOpenAI
from pydantic import BaseModel

# Import agent functions
from agents.clarification_agent import clarification_agent
from agents.cognitive_reasoning_agent import cognitive_reasoning_agent
from agents.claim_decomposition_agent import claim_decomposition_agent
from agents.question_generation_agent import question_generation_agent
from agents.research_agent import research_agent
from agents.analyst_agent import analyst_agent
from agents.argumentation_mining_agent import argumentation_mining_agent
from agents.drafter_agent import drafter_agent
from agents.objectivity_agent import objectivity_agent 
from agents.data_visualization_reporting_agent import data_visualization_reporting_agent
from agents.user_feedback_explanation_agent import user_feedback_explanation_agent
from agents.followup_agent import followup_agent
from tavily import AsyncTavilyClient

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

# Retrieve API keys and Redis configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
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
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    redis_client.ping()
    logger.info(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}, DB: {REDIS_DB}")
except redis.ConnectionError as e:
    logger.error(f"Could not connect to Redis: {e}")
    raise e

# Configure OpenAI API client (using your private API)
openai_client = AsyncOpenAI(
    api_key=OPENAI_API_KEY, #base_url="http://66.56.129.171:7750/v1"
)
# Configure Tavily API client
tavily_client = AsyncTavilyClient(api_key=TAVILY_API_KEY)

# -------------------- Tokenizer -------------------- 
# Tokenizer for gpt-4o (100k context)
try:
    tokenizer = tiktoken.encoding_for_model("gpt-4o")
except:
    tokenizer = tiktoken.get_encoding("gpt-4o")  # Fallback if encoding not found

def count_tokens(text: str) -> int:
    return len(tokenizer.encode(text))

# ------------------------------------------------------

# Define request and response models (if needed)
# ... 

# ----------------------- API Endpoints -----------------------

# WebSocket Endpoint
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    logger.info(f"WebSocket connection established for session ID: {session_id}")

    try:
        while True:
            message = await websocket.receive_json()

            if message["type"] == "new_question":
                data = {
                    "original_question": message["content"],
                    "session_id": session_id,
                }

                # 1. Clarification Agent
                data = await clarification_agent(openai_client, data, websocket)

                # 2. Cognitive Reasoning Agent
                data = await cognitive_reasoning_agent(openai_client, data, websocket)

                # 3. Claim Decomposition Agent
                data = await claim_decomposition_agent(openai_client, data, websocket)

                # 4. Question Generation Agent
                data = await question_generation_agent(openai_client, data, websocket)

                # *** FILTER QUESTIONS ***
                research_questions = data.get("research_questions", [])
                valid_questions = [q for q in research_questions if 4 < len(q.strip()) < 400]
                data["research_questions"] = valid_questions[:25] # Limit to 25 valid questions

                # 5. Research Agent
                data = await research_agent(openai_client, data, websocket)

                # 6. Analyst Agent
                data = await analyst_agent(openai_client, data, websocket)

                # 7. Argumentation Mining Agent
                data = await argumentation_mining_agent(openai_client, data, websocket)

                # 8. Drafter Agent
                data = await drafter_agent(openai_client, data, websocket)

                # 9. Objectivity Agent (formerly Compliance Agent)
                data = await objectivity_agent(
                    openai_client, data, websocket, redis_client
                )

                # 10. Data Visualization & Reporting Agent
                data = await data_visualization_reporting_agent(
                    openai_client, data, websocket
                )

                # 11. User Feedback & Explanation Agent
                data = await user_feedback_explanation_agent(
                    openai_client, data, websocket
                )

            elif message["type"] == "followup":
                data = {
                    "followup_question": message["content"],
                    "session_id": session_id,
                }
                await followup_agent(
                    openai_client, tavily_client, data, websocket, redis_client
                )

            else:
                logger.warning("Invalid message type received: %s", message["type"])

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_json(
            {"type": "error", "content": f"An error occurred: {str(e)}"}
        )

    finally:
        await websocket.close()
        logger.info(f"WebSocket connection closed for session ID: {session_id}")

# ----------------------- Agent Functions -----------------------

# ... (All agent functions - you can add the max_tokens parameter to the OpenAI API calls) ... 

# Example in chain_of_thought_agent.py:
# response = await openai_client.chat.completions.create(
#     model="gpt-4o",
#     messages=messages,
#     temperature=0.3,
#     max_tokens=16000  # Set max output tokens
# )

# ----------------------- Shutdown Event -----------------------

@app.on_event("shutdown")
async def shutdown_event():
    await openai_client.close()
    logger.info("Shutdown event: Closed OpenAI client.")


# ----------------------- Run Uvicorn Server -----------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="debug")