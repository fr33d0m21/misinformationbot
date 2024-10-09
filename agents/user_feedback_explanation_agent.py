import asyncio
from openai import AsyncOpenAI
import json
import logging
from typing import Dict, Any, List
from fastapi import WebSocket
from dotenv import load_dotenv
import tiktoken

load_dotenv()

logger = logging.getLogger(__name__)

# Tokenizer for gpt-4o (100k context)
try:
    tokenizer = tiktoken.encoding_for_model("gpt-4o")
except:
    tokenizer = tiktoken.get_encoding("gpt-4o")  # Fallback if encoding not found


def count_tokens(text: str) -> int:
    return len(tokenizer.encode(text))


async def user_feedback_explanation_agent(
    openai_client: AsyncOpenAI, data: Dict[str, Any], websocket: WebSocket
) -> Dict[str, Any]:
    try:
        logger.info("Generating user feedback and explanations.")
        await websocket.send_json(
            {"type": "thinking", "content": "Providing Feedback & Explanation..."}
        )
        original_question = data.get("original_question", "")
        clarification = data.get("clarification", "")
        chain_of_thought = data.get("chain_of_thought", "")
        analysis = data.get("analysis", "")
        argumentation_analysis = data.get("argumentation_analysis", "")
        visual_report = data.get("visual_report", "")
        objectivity_feedback = data.get("objectivity_feedback", "")
        research_data = data.get("research_data", {})

        # 1. Chunk Data for Context Window Management
        max_tokens = 8000  # Adjust based on model and cost
        chunks = []

        current_chunk = ""
        current_tokens = 0

        for key, value in data.items():
            if key == "session_id":
                continue  # Skip session ID

            # Convert dictionaries and lists to strings for token counting
            if isinstance(value, (dict, list)):
                value = json.dumps(value)

            value_tokens = count_tokens(
                str(value)
            )  # Count tokens of the string representation

            if current_tokens + value_tokens > max_tokens:
                chunks.append(current_chunk.strip())
                current_chunk = f"{key}: {value}\n\n"
                current_tokens = value_tokens
            else:
                current_chunk += f"{key}: {value}\n\n"
                current_tokens += value_tokens

        if current_chunk:
            chunks.append(current_chunk.strip())

        # 2. Generate Summary and Feedback for Each Chunk
        user_feedback = ""
        for i, chunk in enumerate(chunks):
            messages = [
                {
                    "role": "system",
                    "content": "You are an AI assistant creating a summary of the truth analysis, explaining the process and results in a user-friendly way. Include key insights, evidence, argument evaluation, objectivity feedback, and suggestions for improvement. Focus on clarity and conciseness.",
                },
                {
                    "role": "user",
                    "content": f"Generate a summary of the following truth analysis (Chunk {i+1} of {len(chunks)}):\n\n{chunk}",
                },
            ]

            response = await openai_client.chat.completions.create(
                model="gpt-4o-latest",
                messages=messages,
                temperature=0.5,
                max_tokens=15000,
            )
            user_feedback += response.choices[0].message.content.strip() + "\n\n"

        # 3. Structure and Send Feedback
        user_feedback = f"## Final Summary and User Feedback:\n\n{user_feedback}"

        logger.info("User Feedback & Explanation Agent Output: %s", user_feedback)
        data["user_feedback"] = user_feedback

        await websocket.send_json({"type": "user_feedback", "content": user_feedback})

        data["chain_of_thought"] += (
            "\n- Generated final user feedback and explanations."
        )
        return data

    except Exception as e:
        logger.error(f"Error in UserFeedbackExplanationAgent: {e}")
        raise Exception("User feedback and explanation generation failed.")