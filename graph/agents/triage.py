from graph.state import AgentState
from mcps.canvas import get_todo_items, get_upcoming_events
from mcps.gsuite import list_emails, list_calendar_events

async def triage_node(state: AgentState) -> dict:
    """Collects initial data from Canvas and Gmail to populate the state."""
    # Fetch Canvas to-do items and upcoming events
    canvas_todos = await get_todo_items()
    canvas_events = await get_upcoming_events()
    
    # Fetch emails from primary account
    emails = await list_emails(account="primary", max_results=5)
    
    # Fetch school emails if they exist
    school_emails = []
    try:
        school_emails = await list_emails(account="school", max_results=5)
    except Exception:
        pass # Handle cases where school account isn't configured
        
    # Fetch upcoming calendar events
    calendar_events = await list_calendar_events(account="primary", max_results=5)
    
    return {
        "emails": emails + school_emails,
        "canvas_data": canvas_todos + canvas_events,
        "deadlines": calendar_events
    }
