import hashlib
import os

import markdown2
from langchain_core.messages import AIMessage

from app.cognitive_service.agent_core.graph_state import AgentState
from app.core.constant.path_constant import SHARE_BASE_PATH, SHARE_BASE_URL
from app.core.logger.logger_config import api_logger
from app.external.openai.openai_client import precise_openai_fallbacks

os.makedirs(SHARE_BASE_PATH, exist_ok=True)

def plan_share_action(state: AgentState):
    api_logger.info("마크다운 정보를 HTML로 전환해 저장한 후 결과를 반환합니다.")
    plan_md = state.get("travel_plan_markdown", "")
    if not plan_md:
        return {
            **state,
            "share_url": None,
            "messages": state["messages"] + [AIMessage(content="❌ 공유할 여행 계획이 없습니다.")],
        }

    html_body = markdown2.markdown(plan_md)

    # 2. 파일 저장용 ID 생성
    hash_id = hashlib.md5(plan_md.encode("utf-8")).hexdigest()
    file_name = f"plan_{hash_id}.html"
    file_path = os.path.join(SHARE_BASE_PATH, file_name)

    html_content = f"""<!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>여행 계획 공유</title>
    </head>
    <body>
    {html_body}
    </body>
    </html>
    """

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # 3. 공유 URL 생성
    share_url = f"{SHARE_BASE_URL}/{file_name}"

    precise_openai_fallbacks.invoke(prompt = f"""
        당신은 여행계획에 접근할 수 있는 경로를 마크다운으로 가독성 있게 전달해주는 에이전트입니다.
        제공된 마크다운을 간결하게 요약해주고, 공유 URL을 사용자가 쉽게 접근할 수 있도록 마크다운 형식으로 설명해 주세요.
        
        - 사용 목적: 여행 계획을 공유하기 위한 웹 링크 안내
        - 표현 톤: 친절하고 정돈된 말투
        - 포함 요소: 제목, 링크, 짧은 안내 문구
        
        마크다운 정보: {plan_md}
        공유 URL: {share_url}
        """)

    return {
        **state,
        "share_url": share_url,
        "messages": state["messages"] + [AIMessage(content=f"#####📤 여행 계획이 공유되었습니다!\n\n🔗 {share_url}")],
        "intent": "travel_conversation"
    }