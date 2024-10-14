import os
from typing import Dict, Any

from openai import OpenAI
from swarm import Agent
from swarm.types import Result 
from agents.user_feedback_explanation_agent import feedback_agent
# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# --- Follow-Up Agent ---
def answer_followup(followup_question: str, session_data: Dict[str, Any]) -> str:
    print(f"Answering follow-up question: {followup_question}")
    """Provides accurate and unbiased answers to follow-up questions 
    related to the truth analysis report. Utilizes session data, 
    including the report, visualizations, and objectivity feedback. 
    May conduct additional research using tools if needed.
    """
    # Extract relevant data from session_data
    claim = session_data.get('claim')
    report = session_data.get('draft_report')
    visualizations = session_data.get('visualizations')
    objectivity_feedback = session_data.get('objectivity_feedback')
    
    # Format data for presentation to the LLM
    context = f"Claim: {claim}\nReport: {report}\nVisualizations: {visualizations}\nObjectivity Feedback: {objectivity_feedback}"

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """You are an AI assistant providing detailed and accurate 
                              answers to follow-up questions about truth analysis reports. 
                              Use the provided information to formulate your response, 
                              and maintain objectivity and neutrality. If you need to 
                              conduct additional research, use available tools. """
            },
            {
                "role": "user",
                "content": f"Previous Analysis:\n{context}\n\nFollow-up Question:\n{followup_question}" 
            }
        ],
        temperature=0.3
    )
    print(response.choices[0].message.content.strip())
    return response.choices[0].message.content.strip()

followup_agent = Agent(
    name='Follow-Up Agent',
    instructions='Answer user follow-up questions based on the previous analysis and data.',
    functions=[answer_followup] # No handoff needed
)