import asyncio
from openai import AsyncOpenAI
import json
import logging
from typing import Dict, Any
from fastapi import WebSocket
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

async def objectivity_agent(openai_client: AsyncOpenAI, data: Dict[str, Any], websocket: WebSocket, redis_client) -> Dict[str, Any]:
    try:
        logger.info("Checking for bias and ensuring objectivity.")
        await websocket.send_json({"type": "thinking", "content": "Checking for bias and ensuring objectivity..."})
        original_question = data.get("original_question", "")
        clarification = data.get("clarification", "")
        chain_of_thought = data.get("chain_of_thought", "")
        draft_report = data.get("draft_report", "")
        session_id = data.get("session_id", "default")

        if not draft_report:
            logger.warning("No draft report provided to the objectivity agent.")
            return data

        # 1. Construct Prompt for Objectivity Evaluation
        messages = [
            {
                "role": "system",
                "content": "You are an AI assistant trained to identify bias and promote objectivity in written reports. Your role is to meticulously analyze a report that evaluates the truthfulness of a claim. Focus on:\n\n- **Language Bias:** Identify any language that might be emotionally charged, subjective, or leading.\n- **Evidence Selection Bias:** Check if the report presents a balanced selection of evidence or if it favors one side of the argument.\n- **Logical Fallacies:** Point out any logical fallacies or flaws in reasoning that might introduce bias.\n- **Source Evaluation:**  Assess whether the report critically evaluates the credibility and potential biases of its sources.\n\nProvide specific examples and concrete suggestions for improvement to ensure the report is as neutral and objective as possible.",
            },
            {
                "role": "user",
                "content": f"Analyze the following report for objectivity, providing specific feedback and suggestions for improvement:\n\nOriginal Claim: {original_question}\nClarification: {clarification}\nChain of Thought: {chain_of_thought}\nReport: {draft_report}",
            },
        ]

        # 2. Generate Objectivity Feedback
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.3,  # Lower temperature for more analytical responses
            max_tokens=2000,
        )
        objectivity_feedback = response.choices[0].message.content.strip()

        # 3. Structure and Send Feedback
        if not objectivity_feedback.startswith("#"):
            objectivity_feedback = f"# Objectivity Feedback\n\n{objectivity_feedback}"

        logger.info("Objectivity Agent Output: %s", objectivity_feedback)

        # 4. Send Feedback to Client
        await websocket.send_json({"type": "objectivity_feedback", "content": objectivity_feedback})

        # 5. Store Session Data (if needed)
        if session_id:
            session_data = {
                "report": draft_report,
                "objectivity_feedback": objectivity_feedback,
            }
            redis_client.set(session_id, json.dumps(session_data), ex=86400)
            logger.info(f"Stored session data for session_id: {session_id} in Redis")

        # 6. Update Chain of Thought
        data["chain_of_thought"] += "\n- Evaluated the report for objectivity and provided feedback."
        return data

    except Exception as e:
        logger.error(f"Error in Objectivity Agent: {e}")
        raise Exception("Objectivity check failed.")