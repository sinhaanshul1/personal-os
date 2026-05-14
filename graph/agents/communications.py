from langchain_google_genai import ChatGoogleGenerativeAI
from graph.state import AgentState
from dotenv import load_dotenv

load_dotenv(override=True)

# Initialize the LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

async def communications_node(state: AgentState) -> dict:
    """Handles communications: identifies urgent emails and drafts professional replies."""
    emails = state.get("emails", [])
    
    if not emails:
        return {"email_drafts": []}
    
    # Prompt the LLM to analyze emails and draft replies
    prompt = f"""
    You are a Communications Assistant. Analyze the following emails:
    {emails}
    
    1. Identify any emails that require an urgent reply (e.g., from professors, collaborators, or important services).
    2. Draft a professional and concise reply for the top 2-3 most important emails.
    3. For other emails, provide a 1-sentence summary of why they don't need an immediate reply.
    
    Format your response as a clear list of drafts.
    """
    
    response = await llm.ainvoke(prompt)
    
    return {
        "email_drafts": [
            {
                "raw_drafts": response.content
            }
        ]
    }
