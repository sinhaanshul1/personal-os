from langchain_google_genai import ChatGoogleGenerativeAI
from graph.state import AgentState
from dotenv import load_dotenv
from mcps.gsuite import add_calendar_event

load_dotenv(override=True)

# Initialize the LLM with tools
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
tools = [add_calendar_event]
llm_with_tools = llm.bind_tools(tools)

async def academic_node(state: AgentState) -> dict:
    """Manages academic tasks and can autonomously schedule events in the calendar."""
    canvas_data = state.get("canvas_data", [])
    deadlines = state.get("deadlines", [])
    
    # Construct a comprehensive prompt for the academic coordinator
    prompt = f"""
    You are an expert Academic Coordinator. Your goal is to help a student stay organized and prepared.
    
    Current Academic Data (Canvas):
    {canvas_data}
    
    Upcoming Deadlines/Events:
    {deadlines}
    
    Please provide:
    1. A prioritized list of upcoming deadlines.
    2. A suggested study schedule for the next 2 days to tackle these tasks.
    3. Use the `add_calendar_event` tool to actually schedule the most important study blocks or deadline reminders in the user's calendar.
    4. Three mock quiz questions related to the most pressing assignment or course.
    5. Initial research or helpful links/concepts for the next major assignment.
    
    Be concise but encouraging.
    """
    
    response = await llm_with_tools.ainvoke(prompt)
    
    return {
        "messages": [response],
        "study_schedule": response.content,
        "homework_research": "Initial research and tips are included in the study schedule summary.",
        "quiz_data": {"generated_questions": "Quiz questions are included in the main summary."}
    }
