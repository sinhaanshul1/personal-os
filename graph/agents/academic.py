from langchain_google_genai import ChatGoogleGenerativeAI
from graph.state import AgentState
from dotenv import load_dotenv

load_dotenv(override=True)

# Initialize the LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

async def academic_node(state: AgentState) -> dict:
    """Manages academic tasks: deadlines, study schedules, quizzes, and research."""
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
    3. Three mock quiz questions related to the most pressing assignment or course.
    4. Initial research or helpful links/concepts for the next major assignment.
    
    Be concise but encouraging.
    """
    
    response = await llm.ainvoke(prompt)
    
    # For now, we store the combined insight in study_schedule and research fields
    return {
        "study_schedule": response.content,
        "homework_research": "Initial research and tips are included in the study schedule summary.",
        "quiz_data": {"generated_questions": "Quiz questions are included in the main summary."}
    }
