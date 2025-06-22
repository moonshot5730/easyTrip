import asyncio
import os
import textwrap

import markdown2
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

from app.cognitive_service.agent_core.graph_state import AgentState
from app.core.constant.path_constant import SHARE_BASE_PATH, SHARE_BASE_URL
from app.core.logger.logger_config import api_logger
from app.external.openai.openai_client import precise_openai_fallbacks
from shared.format_util import to_html_format

os.makedirs(SHARE_BASE_PATH, exist_ok=True)


url_share_system_prompt = f"""
    당신은 여행계획에 접근할 수 있는 경로를 마크다운으로 가독성 있게 전달해주는 에이전트입니다.
    사용자가 입력한 마크다운 정보와 URL 정보를 간결하게 요약해주고, 공유 URL을 사용자가 쉽게 접근할 수 있도록 마크다운 형식으로 설명해 주세요.

    - 사용 목적: 여행 계획을 공유하기 위한 웹 링크 안내
    - 표현 톤: 친절하고 정돈된 말투
    - 포함 요소: 제목, 링크, 짧은 안내 문구
    """

def plan_share_action(state: AgentState):
    api_logger.info("마크다운 정보를 HTML로 전환해 저장한 후 결과를 반환합니다.")

    plan_md = state.get("travel_plan_markdown", "")
    session_id = state.get("session_id", "")

    if not plan_md:
        return {
            **state,
            "share_url": None,
            "messages": state["messages"] + [AIMessage(content="❌ 공유할 여행 계획이 없습니다.")],
        }

    html_body = markdown2.markdown(plan_md)

    file_name = f"plan_{session_id}.html"
    file_path = os.path.join(SHARE_BASE_PATH, file_name)

    html_content = to_html_format(html_body)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # 3. 공유 URL 생성
    share_url = f"{SHARE_BASE_URL}/{file_name}"

    messages = [
        SystemMessage(content=url_share_system_prompt),
        HumanMessage(content=textwrap.dedent(f"""
            마크다운 정보: {plan_md}
            공유 URL: {share_url}""").strip())
    ]
    precise_openai_fallbacks.invoke(messages)

    return {
        **state,
        "share_url": share_url,
        "messages": state["messages"] + [AIMessage(content=f"#####📤 여행 계획이 공유되었습니다!\n\n🔗 {share_url}")],
        "intent": "travel_conversation"
    }


if __name__ == "__main__":
    async def run_test():
        plan_md = textwrap.dedent("""# 제주도 여행 일정  
            - 1일차: 성산 일출봉  
            - 2일차: 우도 투어  
            - 3일차: 한라산 등반""")

        test_state = {
            "session_id": "test-session-123",
            "travel_plan_markdown": plan_md,
            "messages": [],
        }

        result = plan_share_action(test_state)

        api_logger.info(f"\n📌 공유 URL: {result.get("share_url")}")
        api_logger.info("\n🧾 메시지 기록:")
        for message in result["messages"]:
            api_logger.info(f"{message}")

    asyncio.run(run_test())