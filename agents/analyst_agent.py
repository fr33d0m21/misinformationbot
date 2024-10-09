import asyncio
from openai import AsyncOpenAI
import json
import logging
from typing import Dict, Any
from fastapi import WebSocket
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

async def analyst_agent(openai_client: AsyncOpenAI, data: Dict[str, Any], websocket: WebSocket) -> Dict[str, Any]:
    try:
        logger.info("Analyzing research data.")
        await websocket.send_json({"type": "thinking", "content": "Analyzing research data..."})
        original_question = data.get("original_question", "")
        clarification = data.get("clarification", "")
        chain_of_thought = data.get("chain_of_thought", "")
        research_data = data.get("research_data", {})

        if not research_data:
            logger.warning("No research data provided to the analyst agent.")
            return data

        # 1. Format Research Data for Analysis
        formatted_research_data = ""
        for question, results in research_data.items():
            formatted_research_data += f"## Research Question: {question}\n\n"
            for i, result in enumerate(results):
                formatted_research_data += (
                    f"**Result {i+1} ({result.get('source', 'Unknown')}):**\n"
                    f"- Title: {result.get('title', 'N/A')}\n"
                    f"- URL: {result.get('url', 'N/A')}\n"
                )
                if result.get("snippet"):
                    formatted_research_data += f"- Snippet: {result.get('snippet')}\n"
                if result.get("answer"):
                    formatted_research_data += f"- Answer: {result.get('answer')}\n"
                formatted_research_data += "\n"

        # 2. Construct Prompt with Context
        messages = [
            {
                "role": "system",
                "content": "You are a truth-seeking analyst. Your role is to carefully examine research data gathered from various sources to determine the veracity of a claim. Consider the original claim, clarification, and chain of thought to provide a comprehensive analysis that highlights key insights, evidence supporting or refuting the claim, potential biases, and inconsistencies in the information. Present your analysis in a clear and concise manner.",
            },
            {
                "role": "user",
                "content": f"Analyze the following research data to evaluate the truthfulness of the claim:\n\nOriginal Claim: {original_question}\nClarification: {clarification}\nChain of Thought: {chain_of_thought}\n\nResearch Data:\n{formatted_research_data}",
            },
        ]

        # 3. Generate Analysis
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.3,
            max_tokens=2000,
        )
        analysis = response.choices[0].message.content.strip()
        logger.info("Analyst Agent Output: %s", analysis)
        data["analysis"] = analysis

        # 4. Send Analysis to Client
        
        await websocket.send_json({"type": "analysis", "content": analysis})
        

        # 5. Update Chain of Thought
        data["chain_of_thought"] += "\n- Analyzed the research data and generated a comprehensive analysis."
        return data

    except Exception as e:
        logger.error(f"Error in AnalystAgent: {e}")
        raise Exception("Analysis failed.")