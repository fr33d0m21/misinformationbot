import asyncio
from openai import AsyncOpenAI
from tavily import AsyncTavilyClient
import json
import logging
import os
from typing import Dict, Any
from fastapi import WebSocket
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

# Configure Tavily API
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
tavily_client = AsyncTavilyClient(api_key=TAVILY_API_KEY)

async def followup_agent(openai_client: AsyncOpenAI, tavily_client: AsyncTavilyClient, data: Dict[str, Any], websocket: WebSocket, redis_client) -> Dict[str, Any]:
    try:
        user_input = data["followup_question"]
        session_id = data.get("session_id", "default")
        logger.info(f"Session ID for Follow-Up: {session_id}")
        logger.info("Received follow-up input: %s", user_input)

        # 1. Retrieve Session Data
        stored_data_json = redis_client.get(session_id)
        if not stored_data_json:
            await websocket.send_json(
                {"type": "error", "content": "No existing session found for follow-up questions."}
            )
            return
        stored_data = json.loads(stored_data_json)
        report = stored_data.get("report", "")
        objectivity_feedback = stored_data.get("objectivity_feedback", "")

        # 2. Optional: Perform Additional Research with Tavily (using free tier)
        tavily_domains = [
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
        
        tavily_response = await tavily_client.search(
            user_input,
            search_depth="advanced",
            max_results=5,  # Limit results to stay within free tier
            include_answer=True,
            include_raw_content=False,
            include_domains=tavily_domains,
        )

        followup_research = ""
        if tavily_response and tavily_response.get("results"):
            followup_research = "\n\n## Additional Research:\n\n"
            for result in tavily_response["results"]:
                followup_research += f"- **{result.get('title', 'N/A')}** ({result.get('source', 'N/A')}): {result.get('url', 'N/A')}\n"
                if result.get('snippet'):
                    followup_research += f"  > {result.get('snippet')}\n"
                if result.get('answer'):
                    followup_research += f"  > **Answer:** {result.get('answer')}\n\n"

        # 3. Construct Prompt for Follow-up Response
        messages = [
            {
                "role": "system",
                "content": "You are an AI assistant providing accurate and unbiased answers to follow-up questions related to truth analysis reports. Utilize the initial report, objectivity feedback, and any additional research to formulate a comprehensive and relevant response grounded in evidence and presented neutrally.",
            },
            {
                "role": "user",
                "content": f"Based on the previous analysis and any additional research, answer this follow-up question:\n\nPrevious Analysis:\n{report}\nObjectivity Feedback:\n{objectivity_feedback}{followup_research}\nFollow-up Question:\n{user_input}",
            },
        ]

        # 4. Generate Follow-up Response
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.3,
            max_tokens=1500,
        )

        followup_response = response.choices[0].message.content.strip()
        logger.info("Follow-Up Agent Output: %s", followup_response)

        # 5. Structure and Send Response
        if not followup_response.startswith("#"):
            followup_response = f"# Follow-Up Response\n\n{followup_response}"

        await websocket.send_json({"type": "followup_response", "content": followup_response})

    except Exception as e:
        logger.error(f"Error in FollowupAgent: {e}")
        raise Exception("Follow-up failed.")