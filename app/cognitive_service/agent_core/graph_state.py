from typing import Annotated, Dict, List, Optional, TypedDict, Literal

from langgraph.graph import add_messages


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


    intent: Literal["tavel_conversation", "search"]

    travel_place: Optional[str]
    travel_schedule: Optional[str]
    travel_style: Optional[str]
    need_place_search: Optional[bool]

    travel_conversation_raw_output: Optional[str]
    travel_conversation_json_output: Optional[dict]

    travel_plan: Optional[dict]

    tavily_search_result: Optional[List[dict]]
    share_url: Optional[str]

