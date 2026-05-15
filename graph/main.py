import asyncio
from typing import Literal
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from graph.state import AgentState
from graph.agents.triage import triage_node
from graph.agents.academic import academic_node
from graph.agents.communications import communications_node
from graph.agents.synthesis import synthesis_node
from mcps.gsuite import create_draft, add_calendar_event

# Define the tools
tools = [create_draft, add_calendar_event]
tool_node = ToolNode(tools)

def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    """Determines if the graph should transition to tools or end a branch."""
    messages = state.get("messages", [])
    if not messages:
        return "__end__"
    last_message = messages[-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "__end__"

# Create the LangGraph StateGraph
workflow = StateGraph(AgentState)

# Register nodes in the graph
workflow.add_node("triage", triage_node)
workflow.add_node("academic", academic_node)
workflow.add_node("communications", communications_node)
workflow.add_node("synthesis", synthesis_node)
workflow.add_node("tools", tool_node)

# Define the execution flow with tool awareness
workflow.add_edge(START, "triage")
workflow.add_edge("triage", "academic")

# Academic can call tools
workflow.add_conditional_edges("academic", should_continue, {
    "tools": "tools",
    "__end__": "communications"
})

# After tools from academic, go to communications
workflow.add_edge("tools", "communications")

# Communications can call tools
workflow.add_conditional_edges("communications", should_continue, {
    "tools": "comm_tools",
    "__end__": "synthesis"
})

# Special node for communications tools to avoid cycles or routing confusion
workflow.add_node("comm_tools", tool_node)
workflow.add_edge("comm_tools", "synthesis")

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
