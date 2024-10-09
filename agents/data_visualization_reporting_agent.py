import asyncio
from openai import AsyncOpenAI
import json
import logging
from typing import Dict, Any, List
from fastapi import WebSocket
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

async def data_visualization_reporting_agent(openai_client: AsyncOpenAI, data: Dict[str, Any], websocket: WebSocket) -> Dict[str, Any]:
    try:
        logger.info("Generating data visualizations and reports.")
        await websocket.send_json({"type": "thinking", "content": "Creating Data Visualization & Report..."})
        original_question = data.get("original_question", "")
        clarification = data.get("clarification", "")
        chain_of_thought = data.get("chain_of_thought", "")
        analysis = data.get("analysis", "")
        argumentation_analysis = data.get("argumentation_analysis", "")
        research_data = data.get("research_data", {})
        objectivity_feedback = data.get("objectivity_feedback", "")

        # 1. Prepare Data for Timeline Visualization
        timeline_data = []
        timeline_data.append(
            {
                "date": "Now",  # Replace with actual date
                "type": "claim",
                "title": "Original Claim",
                "description": original_question,
                "source": "User",
            }
        )

        for question, results in research_data.items():
            for result in results:
                timeline_data.append(
                    {
                        "date": result.get("date", "Unknown"), 
                        "type": "research",
                        "title": result.get("title"),
                        "description": result.get("snippet"),
                        "url": result.get("url"),
                        "source": result.get("source"),
                    }
                )

        d3_data = {"events": timeline_data}
        data["d3_data"] = json.dumps(d3_data)  

        # 2. Generate Description of D3.js Timeline
        timeline_description = """
        ## Interactive Timeline Visualization (D3.js)

        Create an interactive timeline visualization using D3.js to represent the events related to the claim. The visualization should include the following elements:

        - **Event Markers:** Represent each event (original claim and research results) as a circle on the timeline.
        - **Color-coding:** Use different colors for event types (claim, research) and potentially for source credibility (if available).
        - **Source Clustering:** Group events from the same source together. 
        - **Tooltip:** Display event details (title, description, URL, source) in a tooltip when hovering over an event marker. 
        - **Zooming and Panning:** Allow users to zoom and pan the timeline for better navigation.
        """

        # 3. Provide D3.js Code Template
        d3_code_template = """
        <div id="timeline"></div>
        <script>
        // Access the timeline data from 'd3_data' (sent from backend)
        const timelineData = JSON.parse(d3_data).events;

        // Set the dimensions and margins of the graph
        const margin = { top: 20, right: 20, bottom: 30, left: 40 },
            width = 960 - margin.left - margin.right,
            height = 300 - margin.top - margin.bottom;

        // Parse the date / time (you might need to adjust the date format)
        const parseDate = d3.timeParse("%Y-%m-%d"); 

        // Create the SVG canvas
        const svg = d3.select("#timeline").append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        // ... (Add more D3.js code here to create the timeline) ...

        </script>
        """

        # 4. Construct the Report
        visual_report = f"""
        ## Data Visualization and Report:

        {timeline_description}

        ### D3.js Code Template:

        ```html
        {d3_code_template}
        ``` 
        
        (Add other visualizations and their descriptions here)
        """

        logger.info("Data Visualization & Reporting Agent Output: %s", visual_report)
        data["visual_report"] = visual_report

        # 5. Send Report to Client
        await websocket.send_json({"type": "visual_report", "content": visual_report})

        data["chain_of_thought"] += "\n- Generated data visualizations and a report with visualization instructions." 
        return data

    except Exception as e:
        logger.error(f"Error in DataVisualizationReportingAgent: {e}")
        raise Exception("Data visualization and reporting failed.")