import asyncio
from langgraph.graph import StateGraph, START, END
from graph.state import AgentState
from graph.agents.triage import triage_node
from graph.agents.academic import academic_node
from graph.agents.communications import communications_node
from graph.agents.synthesis import synthesis_node

# Create the LangGraph StateGraph
workflow = StateGraph(AgentState)

# Register nodes in the graph
workflow.add_node("triage", triage_node)
workflow.add_node("academic", academic_node)
workflow.add_node("communications", communications_node)
workflow.add_node("synthesis", synthesis_node)

# Define the execution flow (Sequential for this architecture)
workflow.add_edge(START, "triage")
workflow.add_edge("triage", "academic")
workflow.add_edge("academic", "communications")
workflow.add_edge("communications", "synthesis")
workflow.add_edge("synthesis", END)

# Compile the graph into a runnable application
app = workflow.compile()

async def run_personal_assistant():
    """Run the assistant graph and print the daily report."""
    initial_state = {
        "messages": [],
        "emails": [],
        "canvas_data": [],
        "deadlines": [],
        "study_schedule": "",
        "quiz_data": {},
        "homework_research": "",
        "email_drafts": [],
        "daily_report": ""
    }
    
    print("🚀 Initializing Personal Assistant Graph...")
    final_state = await app.ainvoke(initial_state)
    
    print("\n" + "═"*50)
    print("📋 FINAL DAILY REPORT")
    print("═"*50)
    print(final_state.get("daily_report", "No report generated."))
    print("═"*50)

if __name__ == "__main__":
    try:
        asyncio.run(run_personal_assistant())
    except Exception as e:
        print(f"❌ Error running graph: {e}")
