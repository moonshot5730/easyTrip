from typing import TypedDict, List, Optional, Annotated, Dict

from langgraph.graph import add_messages


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    action: Optional[str]
    keywords: Optional[List[str]]

    want_travel_city: Optional[str]
    travel_schedule: Optional[str]
    travel_style: Optional[str]

    search_results: List[Dict[str, str]]


