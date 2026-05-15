from langchain_google_genai import ChatGoogleGenerativeAI
from graph.state import AgentState
from dotenv import load_dotenv
from mcps.gsuite import create_draft

load_dotenv(override=True)

# Initialize the LLM with tools
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
tools = [create_draft]
llm_with_tools = llm.bind_tools(tools)

async def communications_node(state: AgentState) -> dict:
    """Handles communications: identifies urgent emails and can autonomously create drafts."""
    emails = state.get("emails", [])
    
    if not emails:
        return {"email_drafts": []}
    
    # Prompt the LLM to analyze emails and call the create_draft tool if necessary
    prompt = f"""
    You are a Communications Assistant. Analyze the following emails:
    {emails}
    
    1. Identify any emails that require an urgent reply (e.g., from professors, collaborators, or important services).
    2. For the most important emails, use the `create_draft` tool to actually create a draft in the user's Gmail.
    3. If you decide to create a draft, inform the user in your text response which emails you've handled.
    4. For other emails, provide a 1-sentence summary of why they don't need an immediate reply.
    5. Do NOT use any emojis in your response.
    """
    
    response = await llm_with_tools.ainvoke(prompt)
    
    # In LangGraph with ToolNode, we need to return the message so the graph can route it
    return {
        "messages": [response],
        "email_drafts": [{"raw_drafts": response.content}]
    }
