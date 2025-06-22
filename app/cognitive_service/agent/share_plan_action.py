import hashlib
import os

import markdown2
from langchain_core.messages import AIMessage

from app.cognitive_service.agent_core.graph_state import AgentState
from app.core.constant.path_constant import SHARE_BASE_PATH, SHARE_BASE_URL

os.makedirs(SHARE_BASE_PATH, exist_ok=True)

def plan_share_action(state: AgentState):
    plan_md = state.get("travel_plan_markdown", "")
    if not plan_md:
        return {
            **state,
            "share_url": None,
            "messages": state["messages"] + [AIMessage(content="❌ 공유할 여행 계획이 없습니다.")],
        }

    html_content = markdown2.markdown(plan_md)

    # 2. 파일 저장용 ID 생성
    hash_id = hashlib.md5(plan_md.encode("utf-8")).hexdigest()
    file_name = f"plan_{hash_id}.html"
    file_path = os.path.join(SHARE_BASE_PATH, file_name)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # 3. 공유 URL 생성
    share_url = f"{SHARE_BASE_URL}/{file_name}"

    return {
        **state,
        "share_url": share_url,
        "messages": state["messages"] + [AIMessage(content=f"{plan_md}\n\n#####📤 여행 계획이 공유되었습니다!\n\n🔗 {share_url}")],
    }