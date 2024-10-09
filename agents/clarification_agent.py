import asyncio
from openai import AsyncOpenAI
import logging
from typing import Dict, Any
from fastapi import WebSocket
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

async def clarification_agent(openai_client: AsyncOpenAI, data: Dict[str, Any], websocket: WebSocket) -> Dict[str, Any]:
    try:
        original_question = data.get("original_question", "")

        # 1. Initial Rephrasing for Clarity
        rephrase_messages = [
            {
                "role": "system",
                "content": "You are an AI assistant skilled in rephrasing statements for clarity and neutrality. Your task is to take a user's input and rephrase it in a clear, concise, and unbiased manner, ensuring that the essential meaning is preserved while removing any emotional charge or leading language.",
            },
            {
                "role": "user",
                "content": f"Rephrase the following statement in a clear and neutral way, focusing on the core issue or question:\n\nStatement: {original_question}",
            },
        ]
        rephrase_response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=rephrase_messages,
            temperature=0.3,  
            max_tokens=1000,
        )
        rephrased_question = rephrase_response.choices[0].message.content.strip()

        # 2. Generate Arguments For and Against
        argument_messages = [
            {
                "role": "system",
                "content": "You are an AI assistant skilled in generating arguments for and against a claim. Your task is to provide a concise and persuasive argument in favor of the claim and a separate concise and persuasive argument against the claim. These arguments should be based on logical reasoning and common knowledge, avoiding any personal opinions or beliefs.",
            },
            {
                "role": "user",
                "content": f"Generate one argument in favor of and one argument against the following claim:\n\nClaim: {rephrased_question}",
            },
        ]
        argument_response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=argument_messages,
            temperature=0.7,  
            max_tokens=1000,
        )
        arguments = argument_response.choices[0].message.content.strip()

        # 3. Structure and Combine the Output
        clarification = (
            f"## Clarification:\n\n"
            f"**Original Claim:** {original_question}\n\n"
            f"**Rephrased Claim:** {rephrased_question}\n\n"
            f"**Arguments For and Against:**\n{arguments}"
        )

        logger.info("Clarification Agent Output: %s", clarification)

        # 4. Send clarification to the client via WebSocket
        await websocket.send_json({"type": "clarification", "content": clarification})

        data["clarification"] = clarification
        return data

    except Exception as e:
        logger.error(f"Error in ClarificationAgent: {e}")
        raise Exception("Claim clarification failed.")