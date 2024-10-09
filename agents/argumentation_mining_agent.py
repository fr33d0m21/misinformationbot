import asyncio
from openai import AsyncOpenAI
import json
import logging
from typing import Dict, Any
from fastapi import WebSocket
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

async def argumentation_mining_agent(openai_client: AsyncOpenAI, data: Dict[str, Any], websocket: WebSocket) -> Dict[str, Any]:
    try:
        logger.info("Mining arguments and evidence.")
        original_question = data.get("original_question", "")
        clarification = data.get("clarification", "")
        chain_of_thought = data.get("chain_of_thought", "")
        analysis = data.get("analysis", "")  # Include the analysis from the analyst_agent
        research_data = data.get("research_data", {})

        if not research_data or not analysis:
            logger.warning("Insufficient data for argumentation mining.")
            return data

        # 1. Format Research Data for Argumentation Mining
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
                "content": "You are an AI assistant skilled in argumentation mining. Your task is to identify and analyze arguments and evidence from the provided research data, considering the initial analysis. Extract the main arguments for and against the claim, highlighting the supporting evidence and evaluating the strength and weaknesses of each argument. Focus on:\n\n- **Identifying Premises and Conclusions:** Clearly state the premises (reasons) and conclusions of each argument.\n- **Evidence Evaluation:** Assess the quality and relevance of the evidence supporting each argument.\n- **Logical Fallacies:** Identify any logical fallacies or flaws in the reasoning.\n- **Bias Detection:** Consider potential biases in the sources or the arguments themselves.",
            },
            {
                "role": "user",
                "content": f"Analyze the following claim, research data, and analysis to identify arguments and evidence:\n\nOriginal Claim: {original_question}\nClarification: {clarification}\nChain of Thought: {chain_of_thought}\nAnalysis: {analysis}\n\nResearch Data:\n{formatted_research_data}",
            },
        ]

        # 3. Generate Argumentation Analysis
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.3,
            max_tokens=2000,
        )
        argumentation_analysis = response.choices[0].message.content.strip()

        logger.info("Argumentation Mining Agent Output: %s", argumentation_analysis)
        data["argumentation_analysis"] = argumentation_analysis
        data["chain_of_thought"] += "\n- Mined and analyzed arguments and evidence from the research data."

        return data

    except Exception as e:
        logger.error(f"Error in ArgumentationMiningAgent: {e}")
        raise Exception("Argumentation mining failed.")