import sys
import uuid
from pathlib import Path

import requests

# 스트림릿 스크립트 실행을 위해서 시스템 경로 root로 지정하는 코드
root_path = str(Path(__file__).resolve().parent.parent)
sys.path.append(root_path)

import streamlit as st

from frontend.ui_component.chat_history_ui import render_chat_history
from shared.event_constant import DATA_TAG, END_MSG, STEP_TAG
from frontend.client_constant.trip_api_constant import START_MESSAGE

st.set_page_config(page_title="🦜🔗 스트림릿 비동기 테스트", layout="centered")
st.title("🔁 SSE 기반 LLM 챗봇")


def init_session_state():
    if "session_id" not in st.session_state:
        reset_session()

    if "messages" not in st.session_state:
        st.session_state.messages = [START_MESSAGE]


def reset_session():
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = [START_MESSAGE]


init_session_state()
st.sidebar.markdown(f"## **현재 세션 ID:** \n`{st.session_state.session_id}`")

if st.sidebar.button("새로운 대화 시작 (세션 초기화)"):
    reset_session()
    st.rerun()


with st.sidebar.expander("🔎 현재 LangGraph 상태"):
    # 버튼 클릭 시 API 호출
    if st.button("📡 LangGraph 상태 새로고침"):
        try:
            # 예: FastAPI의 /graph-state endpoint 호출
            response = requests.post("http://localhost:8000/graph-state", json={
                "session_id": st.session_state.session_id,
                "messages": st.session_state.messages,
            })
            response.raise_for_status()
            st.session_state.graph_state = response.json()
        except Exception as e:
            st.error(f"상태 요청 실패: {e}")

    # 상태 정보 출력
    graph_state = st.session_state.get("graph_state")
    if graph_state:
        st.json(graph_state)
    else:
        st.write("상태 없음")

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

        payload = {
            "messages": st.session_state["messages"],
            "session_id": st.session_state.session_id,
        }
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
