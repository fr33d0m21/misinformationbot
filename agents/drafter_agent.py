import asyncio
from openai import AsyncOpenAI
import logging
from typing import Dict, Any
from fastapi import WebSocket
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

async def drafter_agent(openai_client: AsyncOpenAI, data: Dict[str, Any], websocket: WebSocket) -> Dict[str, Any]:
    try:
        logger.info("Drafting the report.")
        await websocket.send_json({"type": "thinking", "content": "Drafting report..."})
        original_question = data.get("original_question", "")
        clarification = data.get("clarification", "")
        chain_of_thought = data.get("chain_of_thought", "")
        analysis = data.get("analysis", "")
        argumentation_analysis = data.get("argumentation_analysis", "")
        research_questions = data.get("research_questions", [])
        research_data = data.get("research_data", {})

        # 1. Format Research Data for the Report
        formatted_research_data = ""
        for question, results in research_data.items():
            formatted_research_data += f"### Research Question: {question}\n\n"
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
                "content": "You are an AI assistant that generates detailed, unbiased, and well-structured reports summarizing truth analyses. Your reports should include the following sections:\n\n- **Claim:** The original claim being analyzed.\n- **Clarification:**  A rephrased and clarified version of the claim.\n- **Chain of Thought:** The cognitive reasoning steps used to analyze the claim.\n- **Research Questions:** The questions used to guide the research.\n- **Research Findings:** A summary of the key information and evidence found.\n- **Argumentation Analysis:**  An evaluation of arguments for and against the claim.\n- **Analysis:** An overall analysis of the claim's truthfulness.\n- **Conclusion:** A concise conclusion based on the analysis.\n\nEnsure the report is written in clear and concise language, using Markdown formatting for readability.",
            },
            {
                "role": "user",
                "content": f"Generate a report based on the following analysis:\n\nOriginal Claim: {original_question}\nClarification: {clarification}\nChain of Thought: {chain_of_thought}\nResearch Questions:\n{chr(10).join(['- ' + q for q in research_questions])}\nResearch Findings:\n{formatted_research_data}\nArgumentation Analysis: {argumentation_analysis}\nAnalysis: {analysis}",
            },
        ]

        # 3. Generate Report
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.3,
            max_tokens=3000,
        )
        report = response.choices[0].message.content.strip()
        logger.info("Drafter Agent Output: %s", report)
        data["draft_report"] = report

        # 4. Send Report to Client
        await websocket.send_json({"type": "draft_report", "content": report})

        # 5. Update Chain of Thought
        data["chain_of_thought"] += "\n- Generated a comprehensive report summarizing the truth analysis."
        return data

    except Exception as e:
        logger.error(f"Error in DrafterAgent: {e}")
        raise Exception("Drafting failed.")