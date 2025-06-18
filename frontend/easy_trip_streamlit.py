import sys
from pathlib import Path

import requests

# 스트림릿 스크립트 실행을 위해서 시스템 경로 root로 지정하는 코드
root_path = str(Path(__file__).resolve().parent.parent)
sys.path.append(root_path)
print(f"Root path: {root_path}")

from shared.event_constant import END_MSG, DATA_TAG, STEP_TAG
import streamlit as st

from frontend.ui_component.chat_history_ui import render_chat_history

st.title("🔁 SSE 기반 LLM 챗봇")

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요?"}
    ]

# UI 렌더링
render_chat_history(st.session_state.messages)

# 사용자 입력
if prompt := st.chat_input("메시지를 입력하세요"):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 스트리밍 응답 영역
    with st.chat_message("assistant"):
        # 스트리밍 응답을 실시간으로 표시할 영역 확보
        full_response = st.empty()
        collected = ""

        # 백엔드 클라이언트를 통해 응답 스트림 받기
        with requests.post(
            "http://localhost:8000//trip/plan/astream-event",
            json={"messages": st.session_state["messages"]},
            stream=True,
            headers={"Accept": "text/event-stream"},
        ) as resp:
            for line in resp.iter_lines(decode_unicode=True):
                if not line:
                    continue

                if line.startswith(f"{STEP_TAG} "):
                    step_info = line.removeprefix(f"{STEP_TAG} ")
                    collected += f"\n\n##### 🧭 {step_info}\n\n"
                    full_response.markdown(collected.strip())

                elif line.startswith(f"{DATA_TAG} "):
                    print(f"데이터 라인 {line}")
                    content = line.removeprefix(f"{DATA_TAG} ").strip()
                    if content == END_MSG:
                        break
                    collected += content
                    full_response.markdown(collected.strip())

        st.session_state["messages"].append(
            {"role": "assistant", "content": collected.strip()}
        )
