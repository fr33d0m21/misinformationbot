import asyncio
import logging
import os
from typing import Dict, Any, List
import json

from openai import AsyncOpenAI
from fastapi import WebSocket
from tavily import AsyncTavilyClient
import requests
from dotenv import load_dotenv

load_dotenv()

# Configure Data.gov API (using requests)
DATAGOV_API_KEY = os.getenv("DATAGOV_API_KEY")
DATAGOV_API_URL = "https://api.data.gov/v1.1/search"

# Configure Tavily API
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
tavily_client = AsyncTavilyClient(api_key=TAVILY_API_KEY)

logger = logging.getLogger(__name__)


async def research_agent(
    openai_client: AsyncOpenAI, data: Dict[str, Any], websocket: WebSocket
) -> Dict[str, Any]:
    try:
        logger.info("Conducting research using various government sources.")
        await websocket.send_json(
            {"type": "thinking", "content": "Conducting research using various government sources..."}
        )
        research_questions = data.get("research_questions", [])

        # *** FILTER QUESTIONS HERE ***
        research_questions = data.get("research_questions", [])
        valid_questions = [q for q in research_questions if 4 < len(q.strip()) < 400]
        data["research_questions"] = valid_questions[:25]  # Limit to 25 valid questions

        if not valid_questions:
            logger.warning("No valid research questions found after filtering.")
            return data

        research_data = {}
        sources = []

        for i, question in enumerate(valid_questions):
            # Send research question to client
            await websocket.send_json({"type": "research_question", "content": question})

            results_data = []

            # 1. Search using Tavily API (limited to specific .gov websites)
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

            logger.debug(f"Sending Tavily query for question: {question}")
            try:
                tavily_response = await tavily_client.search(
                    question,
                    search_depth="advanced",
                    max_results=5,  # Reduce max results for Tavily
                    include_answer=True,
                    include_raw_content=False,
                    include_domains=tavily_domains,
                )

                logger.debug(
                    f"Tavily response for question '{question}': {tavily_response}"
                )
                print(
                    f"Tavily response for question '{question}': {tavily_response}"
                )  # Print to console as well

                if tavily_response and tavily_response.get("results"):
                    logger.debug(
                        f"Received {len(tavily_response['results'])} results from Tavily."
                    )
                    for j, result in enumerate(tavily_response["results"]):
                        results_data.append(
                            {
                                "title": result.get("title"),
                                "url": result.get("url"),
                                "snippet": result.get("snippet"),
                                "content": result.get("content"),
                                "final_answer": result.get("final_answer"),
                                "answer": result.get("answer"),
                                "source": "Tavily",
                            }
                        )
                        sources.append(
                            {"title": result.get("title"), "url": result.get("url")}
                        )

                        # Send each research result to the client via WebSocket
                        await websocket.send_json(
                            {
                                "type": "research_result",
                                "content": json.dumps(result),
                                "final_answer": json.dumps(result.get("final_answer")),
                                "question": question,
                                "question_number": i + 1,
                                "answer_number": j + 1,
                                "source": result.get("source", "final_answer"),
                                "title": result.get("title"),  # Send full title
                            }
                        )

            except Exception as e:
                logger.error(
                    f"Error during Tavily search for question '{question}': {e}"
                )
                print(
                    f"Error during Tavily search for question '{question}': {e}"
                )  # Print to console
                # ... (handle the error if needed) ...

            # 2. Search using Data.gov API (using requests)
            datagov_params = {
                "q": question,
                "api_key": DATAGOV_API_KEY,
                "rows": 5,  # Adjust as needed
            }
            datagov_response = requests.get(DATAGOV_API_URL, params=datagov_params)

            if datagov_response.status_code == 200:
                datagov_data = datagov_response.json()
                if datagov_data.get("results"):
                    for j, result in enumerate(datagov_data["results"]):
                        results_data.append(
                            {
                                "title": result.get("title"),
                                "url": result.get("landingPage"),
                                "snippet": result.get("description"),
                                "source": "Data.gov",
                            }
                        )
                        sources.append(
                            {
                                "title": result.get("title"),
                                "url": result.get("landingPage"),
                            }
                        )

                        # Send each research result to the client via WebSocket
                        await websocket.send_json(
                            {
                                "type": "research_result",
                                "content": json.dumps(result),  # Send the result as JSON
                                "question": question,  # Add the question to the result
                                "question_number": i + 1,  # Add the question number
                                "answer_number": j + 1,  # Add the answer number
                                "title": result.get("title"),  # Send full title
                            }
                        )

            research_data[question] = results_data

            await asyncio.sleep(1)  # Delay to prevent rate limiting

        data["research_data"] = research_data
        data["sources"] = sources
        return data

    except Exception as e:
        logger.error(f"Error in ResearchAgent: {e}")
        raise Exception(f"Research failed: {str(e)}")