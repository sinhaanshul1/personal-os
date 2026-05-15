from langchain_google_genai import ChatGoogleGenerativeAI
from graph.state import AgentState
from dotenv import load_dotenv

load_dotenv(override=True)

# Initialize the LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

async def synthesis_node(state: AgentState) -> dict:
    """Synthesizes all agent actions into a comprehensive daily report."""
    study_schedule = state.get("study_schedule", "No schedule generated.")
    email_drafts = state.get("email_drafts", [])
    canvas_data = state.get("canvas_data", [])
    
    # Prompt the LLM to synthesize the results into a report
    prompt = f"""
    You are the Synthesis Agent. Your goal is to provide the user with a final summary of everything the assistant has processed.
    
    Data Processed:
    - Canvas/Academic tasks: {len(canvas_data)} items analyzed.
    - Study Schedule/Insights: {study_schedule}
    - Email Drafts: {email_drafts}
    
    Task:
    Create a "Daily Report" that is professional, clear, and actionable. 
    Use headers for different sections (e.g., Academic Overview, Communications, Next Steps).
    Do NOT use any emojis in your response.
    End with a motivational sign-off.
    """
    
    response = await llm.ainvoke(prompt)
    
    return {
        "daily_report": response.content
    }
