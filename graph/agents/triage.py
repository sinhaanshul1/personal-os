from graph.state import AgentState
from mcps.canvas import get_todo_items, get_upcoming_events
from mcps.gsuite import list_emails, list_calendar_events
from graph.memory import query_memories, add_memories

async def triage_node(state: AgentState) -> dict:
    """Collects initial data and retrieves relevant long-term memories."""
    # 1. Fetch live data
    canvas_todos = await get_todo_items()
    canvas_events = await get_upcoming_events()
    emails = await list_emails(account="primary", max_results=5)
    calendar_events = await list_calendar_events(account="primary", max_results=5)
    
    all_live_data = canvas_todos + canvas_events + emails + calendar_events
    
    # 2. Retrieve relevant memories (contextualizing based on top priority)
    # We search for context related to the current most pressing academic or communication items
    context_query = "upcoming deadlines and urgent communications"
    if canvas_todos:
        context_query = f"Deadlines: {canvas_todos[0].get('title', '')}"
    
    relevant_docs = await query_memories(context_query, k=5)
    past_context = "\n".join([doc.page_content for doc in relevant_docs])
    
    # 3. Index new data for future use (incremental memory)
    # To keep it efficient, we index snippets of the most important data
    new_memories = [f"Event: {e.get('summary') or e.get('title')}" for e in all_live_data if e]
    if new_memories:
        await add_memories(new_memories)

    return {
        "emails": emails,
        "canvas_data": canvas_todos + canvas_events,
        "deadlines": calendar_events,
        "daily_report": f"--- PAST CONTEXT ---\n{past_context}\n--------------------\n" # Pass context to synthesis
    }
