import os
from typing import Dict, Any, List

from openai import OpenAI
from swarm import Agent
from swarm.types import Result 
# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# --- User Feedback & Explanation Agent ---
def generate_feedback(
    claim: str,
    draft_report: str,
    visualizations: str,
    objectivity_feedback: str,
) -> str:
    """Generates a final summary and feedback for the user,
    explaining the analysis process and results in a clear,
    concise, and understandable way. Incorporates visualizations
    and objectivity feedback for a comprehensive explanation.
    """
    print("Generating Feedback...")
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """You are an AI assistant designed to provide clear and concise
                              explanations of truth analysis results to users. Combine the
                              analysis report, visualizations, and objectivity feedback
                              to create a user-friendly final summary and feedback. Address
                              any potential biases highlighted in the objectivity feedback.
                              Your goal is to provide a comprehensive and understandable
                              explanation of the claim's truthfulness.""",
            },
            {
                "role": "user",
                "content": f"Claim: {claim}\nReport: {draft_report}\nVisualizations: {visualizations}\nObjectivity Feedback: {objectivity_feedback}",
            },
        ],
        temperature=0.5,
    )
    user_feedback = response.choices[0].message.content.strip()
    print("User Feedback:", user_feedback)
    return user_feedback


def feedback_handoff(user_feedback: str) -> Result:
    """Handoff function to store the final user feedback in context variables.
    Since this is the last agent, there's no agent to hand off to.
    """
    return Result(
        value="Generated user feedback and explanations.",
        context_variables={"user_feedback": user_feedback},
    )  # No more agents to handoff to


feedback_agent = Agent(
    name="User Feedback Agent",
    instructions="Summarize the analysis process and results in a user-friendly way, providing explanations and suggestions.",
    functions=[generate_feedback, feedback_handoff],
)