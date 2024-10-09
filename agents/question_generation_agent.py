import asyncio
from openai import AsyncOpenAI
import logging
from typing import Dict, Any, List
from fastapi import WebSocket
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

async def question_generation_agent(openai_client: AsyncOpenAI, data: Dict[str, Any], websocket: WebSocket) -> Dict[str, Any]:
    try:
        original_question = data.get("original_question", "")
        clarification = data.get("clarification", "")
        chain_of_thought = data.get("chain_of_thought", "")
        subclaims = data.get("subclaims", [])

        research_questions = []

        # 1. Generate Questions for Each Subclaim
        for i, subclaim in enumerate(subclaims):
            messages = [
                {
                    "role": "system",
                    "content": f"You are a research assistant focused on crafting insightful research questions. Your task is to generate 5 specific, unbiased research questions that can help investigate the truthfulness of a sub-claim, considering the overall context of the original claim, clarification, and chain of thought. Focus on generating questions that can be answered through research using publicly available information and data.",
                },
                {
                    "role": "user",
                    "content": f"Generate 2 research questions for the following sub-claim:\n\nOriginal Claim: {original_question}\nClarification: {clarification}\nChain of Thought: {chain_of_thought}\nSub-claim {i+1}: {subclaim}",
                },
            ]

            response = await openai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.5,
                max_tokens=1000,
            )
            questions_text = response.choices[0].message.content.strip()

            # Extract questions and add to the list
            for line in questions_text.split("\n"):
                line = line.strip()
                if line:
                    line = line.lstrip("1234567890. ").lstrip("- ").strip()
                    research_questions.append(line)

        logger.info("Question Generation Agent Output: %s", research_questions)
        data["research_questions"] = research_questions

        # 2. Update Chain of Thought
        data["chain_of_thought"] += (
            f"\n- **Generated {len(research_questions)} Research Questions:**\n{chr(10).join(['    - ' + q for q in research_questions])}"
        )

        # 3. Send "Thinking" Message
        await websocket.send_json(
            {"type": "thinking", "content": "Generating insightful research questions..."}
        )
        

        return data

    except Exception as e:
        logger.error(f"Error in QuestionGenerationAgent: {e}")
        raise Exception("Question generation failed.")