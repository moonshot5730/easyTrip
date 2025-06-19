import sys
import uuid
from pathlib import Path

import requests

# 스트림릿 스크립트 실행을 위해서 시스템 경로 root로 지정하는 코드
root_path = str(Path(__file__).resolve().parent.parent)
sys.path.append(root_path)

from shared.event_constant import END_MSG, DATA_TAG, STEP_TAG
import streamlit as st

from frontend.ui_component.chat_history_ui import render_chat_history

st.set_page_config(page_title="🦜🔗 스트림릿 비동기 테스트", layout="centered")
st.title("🔁 SSE 기반 LLM 챗봇")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4()) # 새 사용자 세션에 고유 ID 할당
    st.session_state.full_response_text = "" # 스트리밍 중인 전체 텍스트 버퍼

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요?"}
    ]

current_session_id = st.session_state.session_id
st.sidebar.markdown(f"## **현재 세션 ID:** \n`{current_session_id}`")

if st.sidebar.button("새로운 대화 시작 (세션 초기화)"):
    st.session_state.session_id = str(uuid.uuid4()) # 새 ID 할당
    st.session_state["messages"] = [
        {"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요?"}
    ]
    st.session_state.full_response_text = ""
    st.rerun() # 앱 다시 로드하여 새 세션 시작

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
        message_placeholder = st.empty()
        stream_response = ""

        payload = {"messages": st.session_state["messages"], "session_id": current_session_id}
        with requests.post(
            "http://localhost:8000//trip/plan/astream-event",
            json=payload,
            stream=True,
            headers={"Accept": "text/event-stream"},
        ) as se_response:
            for line in se_response.iter_lines(decode_unicode=True):
                if not line:
                    continue

                if line.startswith(f"{STEP_TAG} "):
                    chunk = line.removeprefix(f"{STEP_TAG} ")
                    chunk = chunk.removesuffix("\n\n")

                    if chunk == END_MSG:
                        break

                    stream_response += f"\n\n##### 🧭 {chunk}\n\n"
                    message_placeholder.markdown(stream_response.strip())

                elif line.startswith(f"{DATA_TAG} "):
                    chunk = line.removeprefix(f"{DATA_TAG} ")
                    chunk = chunk.removesuffix("\n\n")

                    if chunk == END_MSG:
                        break
                    stream_response += chunk
                    message_placeholder.markdown(stream_response.strip())

                elif chunk.startswith("search: "):
                    content = chunk.removeprefix("search: ")
                    content = content.removesuffix("\n\n")

                    print(content, end="", flush=True)

                    stream_response += content
                    message_placeholder.markdown(stream_response + " ")
                else:
                    stream_response += chunk

        st.session_state["messages"].append(
            {"role": "assistant", "content": stream_response.strip()}
        )
