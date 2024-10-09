import asyncio
from openai import AsyncOpenAI
import logging
from typing import Dict, Any
from fastapi import WebSocket
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

async def claim_decomposition_agent(openai_client: AsyncOpenAI, data: Dict[str, Any], websocket: WebSocket) -> Dict[str, Any]:
    try:
        original_question = data.get("original_question", "")
        clarification = data.get("clarification", "")
        chain_of_thought = data.get("chain_of_thought", "")

        # 1. Construct Prompt with Context
        messages = [
            {
                "role": "system",
                "content": "You are an AI assistant specialized in decomposing complex claims into smaller, verifiable sub-claims. Consider the provided clarification and chain of thought to identify the most relevant aspects of the claim for decomposition. Focus on generating sub-claims that are specific, measurable, achievable, relevant, and time-bound (SMART).",
            },
            {
                "role": "user",
                "content": f"Decompose the following claim into 5 specific, measurable, achievable, relevant, and time-bound (SMART) sub-claims that can be researched individually:\n\nOriginal Claim: {original_question}\nClarification: {clarification}\nChain of Thought: {chain_of_thought}",
            },
        ]

        # 2. Generate Sub-claims
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.5, 
            max_tokens=1500,
        )
        subclaims_text = response.choices[0].message.content.strip()

        # 3. Extract and Structure Sub-claims
        subclaims = []
        for line in subclaims_text.split("\n"):
            line = line.strip()
            if line:
                # Remove leading numbers or bullets
                line = line.lstrip("1234567890. ").lstrip("- ").strip()
                subclaims.append(line)

        logger.info("Claim Decomposition Agent Output: %s", subclaims)
        data["subclaims"] = subclaims
        data["chain_of_thought"] += (
            f"\n- **Decomposed Claim into Sub-claims:**\n {chr(10).join(['    - ' + sc for sc in subclaims])}"
        )

        # 4. Send "Thinking" Message
        await websocket.send_json({"type": "thinking", "content": "Decomposing the claim into verifiable parts..."})
        await websocket.send_json({"type": "claim_decomposition", "content": '\n'.join(subclaims)})
        await websocket.send_json({"type": "thinking", "content": "Let me break down this claim into smaller parts..."})
        await websocket.send_json({"type": "thinking", "content": "Let me think of some questions to research your statement..."}) 
        return data

    except Exception as e:
        logger.error(f"Error in ClaimDecompositionAgent: {e}")
        raise Exception("Claim decomposition failed.")