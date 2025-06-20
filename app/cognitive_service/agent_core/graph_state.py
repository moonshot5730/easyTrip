from typing import Annotated, Dict, List, Optional, TypedDict

from langgraph.graph import add_messages


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


    intent: Optional[str]

    travel_city: Optional[str]
    travel_style: Optional[str]
    travel_schedule: Optional[str]
    travel_plan: Optional[dict]


    tavily_search_result: Optional[List[dict]]
    share_url: Optional[str]
