import asyncio
from openai import AsyncOpenAI
import logging
from typing import Dict, Any
from fastapi import WebSocket
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

async def cognitive_reasoning_agent(openai_client: AsyncOpenAI, data: Dict[str, Any], websocket: WebSocket) -> Dict[str, Any]:
    try:
        original_question = data.get("original_question", "")
        clarification = data.get("clarification", "")

        # 1. Generate Initial Chain of Thought
        chain_of_thought_messages = [
            {
                "role": "system",
                "content": "You are an AI assistant specializing in generating chains of thought for truth analysis. Your task is to create a structured thought process for analyzing the truthfulness of a claim, considering different perspectives, potential biases, relevant knowledge domains, and logical reasoning steps.",
            },
            {
                "role": "user",
                "content": f"Generate a detailed chain of thought for analyzing the truthfulness of the following claim:\n\nClaim: {original_question}\nClarification: {clarification}",
            },
        ]
        chain_of_thought_response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=chain_of_thought_messages,
            temperature=0.3, 
            max_tokens=2000,
        )
        initial_chain_of_thought = chain_of_thought_response.choices[0].message.content.strip()

        # 2. Enhance with Cognitive Reasoning Prompts
        cognitive_reasoning_messages = [
            {
                "role": "system",
                "content": "You are an AI assistant specialized in applying cognitive reasoning principles to chains of thought. Your task is to enhance the provided chain of thought by incorporating the following cognitive reasoning elements:\n\n- **Deductive Reasoning:** Identify any instances where general principles or rules can be applied to the specific claim to draw logical conclusions.\n- **Inductive Reasoning:**  Look for patterns or trends in the evidence that might support or refute the claim.\n- **Analogical Reasoning:**  Explore whether there are similar cases or analogies that can provide insights into the truthfulness of the claim.\n- **Abductive Reasoning:**  Consider possible explanations for the claim and evaluate which explanation is most likely based on the available evidence.\n- **Causal Reasoning:**  Investigate potential cause-and-effect relationships that might be relevant to the claim.",
            },
            {
                "role": "user",
                "content": f"Enhance the following chain of thought by incorporating the cognitive reasoning elements described above:\n\n{initial_chain_of_thought}",
            },
        ]
        cognitive_reasoning_response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=cognitive_reasoning_messages,
            temperature=0.5, 
            max_tokens=2000,
        )
        enhanced_chain_of_thought = cognitive_reasoning_response.choices[0].message.content.strip()

        # 3. Structure the Output
        final_chain_of_thought = (
            "## Chain of Thought:\n"
            f"- **Original Question:** {original_question}\n"
            f"- **Clarification:** {clarification}\n"
            f"- **Cognitive Reasoning:**\n{enhanced_chain_of_thought}\n"
            "- Generated research questions based on the chain of thought."
        )

        logger.info("Cognitive Reasoning Agent Output: %s", final_chain_of_thought)

        # 4. Send Output with Correct Type
        await websocket.send_json({"type": "cognitive_reasoning", "content": final_chain_of_thought}) # Corrected type

        data["chain_of_thought"] = final_chain_of_thought
        return data

    except Exception as e:
        logger.error(f"Error in CognitiveReasoningAgent: {e}")
        raise Exception("Chain of Thought generation failed.")