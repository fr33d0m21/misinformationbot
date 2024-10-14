import os

from openai import OpenAI
from swarm import Swarm, Agent 
from swarm.types import Result # Import Result from swarm.types

# Correct import to avoid circular import
from agents.data_visualization_reporting_agent import visualization_agent, visualization_handoff
from agents.user_feedback_explanation_agent import feedback_agent, feedback_handoff  

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Objectivity Agent ---
def check_objectivity(draft_report: str, rephrased_claim: str, analysis: str) -> str:
    """Analyzes the draft report for potential biases, using a combination
    of linguistic analysis and reasoning about evidence selection, logical
    fallacies, and source credibility. Provides specific suggestions for
    improving objectivity.
    """
    print("Checking for biases...")
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """You are a highly skilled bias detection and objectivity specialist.
                              Analyze the draft report to ensure it is completely unbiased.  Consider:
                              - Language Bias: Identify emotionally charged, subjective, or leading language.
                              - Evidence Selection Bias:  Check if evidence presentation favors one side.
                              - Logical Fallacies:  Point out any fallacies that might introduce bias.
                              - Source Evaluation: Assess source credibility and potential biases.

                              Provide specific examples and actionable suggestions for improvement.""",
            },
            {
                "role": "user",
                "content": f"Claim: {rephrased_claim}\nAnalysis: {analysis}\nDraft Report: {draft_report}",
            },
        ],
        temperature=0.3,  # Lower temperature for more analytical responses
    )
    objectivity_feedback = response.choices[0].message.content.strip()
    print("Objectivity Feedback:", objectivity_feedback)
    return objectivity_feedback

def objectivity_handoff(objectivity_feedback: str) -> Result:
    """Handoff function to pass objectivity feedback 
    to the Data Visualization Agent. 
    """
    # Get results from visualization_agent
    intermediate_result = visualization_handoff(objectivity_feedback)
    # Extract the visualizations from intermediate_result
    visualizations = intermediate_result.context_variables.get("visualizations")

    # Pass the visualizations to feedback_handoff 
    return feedback_handoff(visualizations)

# Define the agent at the bottom of the file
objectivity_agent = Agent(
    name="Objectivity Agent",
    instructions="Analyze the report for potential biases and provide suggestions for improvement.",
    functions=[check_objectivity, objectivity_handoff],
)