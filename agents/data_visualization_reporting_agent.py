import os
import json
from typing import Dict, Any, List

from openai import OpenAI
from swarm import Swarm, Agent 
from swarm.types import Result # Import Result from swarm.types

from agents.user_feedback_explanation_agent import feedback_agent, feedback_handoff

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# --- Data Visualization Agent ---
def create_timeline_visualization(
    research_data: Dict[str, Any], analysis: str, claim: str, subclaims: List[str]
) -> str:
    """Creates an interactive timeline visualization using D3.js to
    represent the events related to the claim and research process.

    Timeline Events:
      - Claim submission
      - Sub-claim generation
      - Research questions
      - Research results with sources
      - Analysis completion

    Features:
      - Event Markers: Circles or icons on the timeline representing events.
      - Color-Coding: Different colors for event types (e.g., claim, research).
      - Tooltips: Displays event details on hover (title, description, source, URL).
      - Zoom & Pan:  Allows users to navigate and focus on specific time periods.
      - Source Clustering: Groups events from the same source.
      - Filtering: Options to filter events by type or source.
      - Links:  Clickable links to sources (if available).

    Output:
      - JSON data structure containing timeline events.
      - D3.js code template (as a string) to create the visualization.
    """
    print("Creating Timeline Visualizations")
    # 1. Extract Timeline Events from Research Data and Context
    timeline_events = []

    # - Claim Submission Event
    timeline_events.append(
        {
            "date": "Now",  # Replace with actual submission timestamp if available
            "type": "claim",
            "title": "Claim Submitted",
            "description": claim,
            "source": "User",
        }
    )

    # - Sub-claim Events
    for i, subclaim in enumerate(subclaims):
        timeline_events.append(
            {
                "date": "Now",  # Use relative timestamps or sequence if actual timestamps not available
                "type": "subclaim",
                "title": f"Sub-claim {i+1}",
                "description": subclaim,
                "source": "MisinformationBot",
            }
        )

    # - Research Question Events
    for question, results in research_data.items():
        timeline_events.append(
            {
                "date": "Now",  # Use relative timestamps
                "type": "question",
                "title": "Research Question",
                "description": question,
                "source": "MisinformationBot",
            }
        )

        # - Research Result Events (Nested under Questions)
        for result in results:
            date = result.get("date", "Unknown")  # Get date if available from the source
            timeline_events.append(
                {
                    "date": date,
                    "type": "result",
                    "title": result.get("title", "No Title"),
                    "description": result.get("snippet", ""),
                    "source": result.get("source", "Unknown Source"),
                    "url": result.get("url"),  # Add URL if available
                }
            )

    # - Analysis Completion Event
    timeline_events.append(
        {
            "date": "Now",  # Replace with actual analysis completion timestamp
            "type": "analysis",
            "title": "Analysis Completed",
            "description": "The analysis of the claim and research findings has been completed.",
            "source": "MisinformationBot",
        }
    )

    # 2. Generate JSON Data Structure for Timeline
    timeline_data = {"events": timeline_events}
    print("Timeline Data:", timeline_data)

    # 3. Generate D3.js Code Template (as a string)
    d3_code_template = """
    <div id="timeline"></div>
    <script>
    // Access the timeline data from 'timeline_data'
    const timelineData = JSON.parse(timeline_data).events;

    // Set the dimensions and margins of the graph
    const margin = { top: 20, right: 20, bottom: 30, left: 40 },
        width = 960 - margin.left - margin.right,
        height = 500 - margin.top - margin.bottom;

    // Parse the date / time (you might need to adjust the date format)
    const parseDate = d3.timeParse("%Y-%m-%d"); 

    // Create the SVG canvas
    const svg = d3.select("#timeline").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // Create a scale for the X-axis
    const x = d3.scaleTime()
        .domain(d3.extent(timelineData, (d) => parseDate(d.date) || new Date())) // If no date, use current date
        .range([0, width]);

    // Add the X-axis to the SVG
    svg.append("g")
        .attr("transform", `translate(0, ${height})`)
        .call(d3.axisBottom(x));

    // Create a scale for the Y-axis (you'll need to define categories)
    const y = d3.scaleBand()
        .range([0, height])
        .domain(["claim", "subclaim", "question", "result", "analysis"]) 
        .padding(1);

    // Add the Y-axis to the SVG
    svg.append("g")
        .call(d3.axisLeft(y));

    // Add the circles for each event
    svg.selectAll("myCircles")
        .data(timelineData)
        .enter()
        .append("circle")
          .attr("cx", (d) => x(parseDate(d.date) || new Date()))
          .attr("cy", (d) => y(d.type) + y.bandwidth() / 2)
          .attr("r", "7")
          .style("fill", (d) => {
              if (d.type === 'claim') return 'green';
              if (d.type === 'subclaim') return 'blue';
              if (d.type === 'question') return 'yellow';
              if (d.type === 'result') return 'orange';
              if (d.type === 'analysis') return 'red';
              return 'gray'; // Default color
          })
          .attr("stroke", "black")

    // Add tooltips
    svg.selectAll("myCircles")
        .on("mouseover", (event, d) => {
            // Create a tooltip element (you can style it with CSS)
            const tooltip = d3.select("body")
                .append("div")
                .style("opacity", 0)
                .attr("class", "tooltip")
                .style("background-color", "white")
                .style("border", "solid")
                .style("border-width", "2px")
                .style("border-radius", "5px")
                .style("padding", "5px")
                .style("position", "absolute")

            // Set the tooltip content and position
            tooltip
                .html(
                    `<strong>${d.title}</strong><br/>` +
                    `Date: ${d.date ? d.date.toDateString() : 'Unknown'}<br/>` +
                    `Source: ${d.source}<br/>` +
                    (d.url ? `<a href="${d.url}" target="_blank">${d.url}</a>` : '') // Add URL if available
                )
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 28) + "px")

            // Transition for smooth appearance
            tooltip.transition()
                .duration(200)
                .style("opacity", .9);
        })

        .on("mouseout", (event, d) => {
            // Remove the tooltip when the mouse leaves the circle
            d3.select(".tooltip").remove();
        });
    </script>
    """

    print("D3 Code Template:", d3_code_template)
    return f"Data: {json.dumps(timeline_data)}\n\nD3.js Code: {d3_code_template}"

def visualization_handoff(objectivity_feedback: str) -> Result:
    """Handoff function to pass visualizations to the User Feedback Agent.
    """
    return feedback_handoff(objectivity_feedback)

# Define the agent at the bottom of the file
visualization_agent = Agent(
    name="Data Visualization Agent",
    instructions="Generate interactive visualizations to represent the research data and analysis.",
    functions=[create_timeline_visualization, visualization_handoff],
)