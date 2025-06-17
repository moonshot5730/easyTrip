from typing import TypedDict, List, Optional

from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    input: str                              # 사용자 입력 원문
    action: str                             # 라우터가 판단한 액션
    keywords: List[str]                     # 입력에서 추출된 핵심 키워드