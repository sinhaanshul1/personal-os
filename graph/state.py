from typing import Annotated, List, TypedDict, Union
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """The state of the agent graph."""
    messages: Annotated[List[Union[dict, tuple]], add_messages]
    emails: List[dict]
    canvas_data: List[dict]
    deadlines: List[dict]
    study_schedule: str
    quiz_data: dict
    homework_research: str
    email_drafts: List[dict]
    daily_report: str
