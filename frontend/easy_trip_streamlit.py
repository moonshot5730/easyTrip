import json
import sys
import uuid
from pathlib import Path

import requests


# 스트림릿 스크립트 실행을 위해서 시스템 경로 root로 지정하는 코드
root_path = str(Path(__file__).resolve().parent.parent)
sys.path.append(root_path)

import streamlit as st

from frontend.ui_component.chat_history_ui import render_chat_history
from shared.event_constant import SPLIT_PATTEN, SSETag
from shared.datetime_util import get_kst_timestamp_label
from frontend.client_constant.trip_api_constant import START_MESSAGE, LANG_STATE_URL, TRAVEL_API_URL

st.set_page_config(page_title="🦜🔗 스트림릿 비동기 테스트", layout="centered")
st.title("🔁 SSE 기반 LLM 챗봇")


def init_session_state():
    if "session_history" not in st.session_state:
        st.session_state.session_history = []

    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    if "messages" not in st.session_state:
        st.session_state.messages = [START_MESSAGE]


def reset_session():
    prev_session_id = st.session_state.session_id
    st.session_state.session_history.append(
        {
            "session_id": prev_session_id,
            "timestamp": get_kst_timestamp_label()
        }
    )
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = [START_MESSAGE]
    st.rerun()


init_session_state()
current_session_id = st.session_state.session_id
st.sidebar.markdown(f"## **현재 세션 ID:** \n`{current_session_id}`")

if st.sidebar.button("새로운 대화 시작 (세션 초기화)"):
    reset_session()


with st.sidebar.expander("🔎 현재 LangGraph 상태"):
    # 버튼 클릭 시 API 호출
    if st.button("📡 LangGraph 상태 가져오기"):
        try:
            # 예: FastAPI의 /graph-state endpoint 호출
            response = requests.get(LANG_STATE_URL, params={
                "session_id": current_session_id,
            })
            response.raise_for_status()

            st.session_state.graph_state = response.json()
            st.success("✅ 상태 정보 가져오기 완료!")
        except Exception as e:
            st.error(f"상태 요청 실패: {e}")

    # 상태 정보 출력
    graph_state = st.session_state.get("graph_state")
    if graph_state:
        st.json(graph_state)
    else:
        st.write("상태 없음")

with st.sidebar.expander("🕘 세션 히스토리", expanded=False):
    history = st.session_state.get("session_history", [])
    if not history:
        st.write("히스토리가 없습니다.")
    else:
        for i, entry in enumerate(reversed(history), 1):
            st.markdown(f"**{i}. {entry["timestamp"]}. 세션 ID:** `{entry['session_id']}`")

# UI 렌더링
render_chat_history(st.session_state.messages)


def parsing_event(event, tag_name: str):
    return event.removeprefix(f"{tag_name}").removesuffix(f"{SPLIT_PATTEN}")


# 사용자 입력
if prompt := st.chat_input("메시지를 입력하세요"):
    chat_request = {"role": "user", "content": prompt}
    st.session_state["messages"].append(chat_request)

    with st.chat_message("user"):
        st.markdown(prompt)

    # 스트리밍 응답 영역
    with st.chat_message("assistant"):
        # 스트리밍 응답을 실시간으로 표시할 영역 확보
        message_placeholder = st.empty()
        status_placeholder = st.empty()

        buffer = ""

        payload = {
            "message": chat_request,
            "session_id": current_session_id,
        }
        with requests.post(
            TRAVEL_API_URL,
            json=payload,
            stream=True,
            headers={"Accept": "text/event-stream"},
        ) as sse_response:
            for event in sse_response.iter_content(chunk_size=None, decode_unicode=True):
                if not event:
                    continue

                if event.startswith(SSETag.CHAT):
                    content = parsing_event(event=event, tag_name=SSETag.CHAT)

                    if "__END__" in content:
                        end_chat_msg = "\n\n응답이 완료되었습니다.\n\n"
                        status_placeholder.info(f"{end_chat_msg}")
                        message_placeholder.markdown(buffer + " ")
                        break

                elif event.startswith(SSETag.STREAM):
                    chunk = parsing_event(event=event, tag_name=SSETag.STREAM)

                    if "__DONE__" in chunk:
                        buffer += "\n\n"
                        message_placeholder.markdown(buffer)
                        continue

                    buffer += chunk
                    message_placeholder.markdown(buffer)

                elif event.startswith(SSETag.NODE):
                    json_str = parsing_event(event=event, tag_name=SSETag.NODE)

                    try:
                        parsed = json.loads(json_str)
                        event_type = parsed.get("event_type", "UNKNOWN")
                        name = parsed.get("name", "알 수 없음")
                        status = parsed.get("status", "")

                        # 상태 표시 (대화 상단)
                        status_placeholder.info(f"🧠 `{name}` → {status}")
                        message_placeholder.markdown(buffer + " ")

                    except json.JSONDecodeError:
                        print("❌ JSON 파싱 오류:", json_str)

                elif event.startswith(SSETag.TOOL):
                    json_str = parsing_event(event=event, tag_name=SSETag.TOOL)

                    try:
                        parsed = json.loads(json_str)
                        event_type = parsed.get("event_type", "UNKNOWN")
                        name = parsed.get("name", "알 수 없음")
                        status = parsed.get("status", "")

                        # 상태 표시 (대화 상단)
                        status_placeholder.info(f"🧠 `{name}` → {status}")
                        message_placeholder.markdown(buffer + " ")

                    except json.JSONDecodeError:
                        print("❌ JSON 파싱 오류:", json_str)

                elif event.startswith(SSETag.SEARCH):
                    content = parsing_event(event=event, tag_name=SSETag.SEARCH)

                    buffer += content
                    status_placeholder.info(f"🧠 현재 처리 노드: `{content}`")
                    message_placeholder.markdown(buffer + " ")

                else:
                    buffer += event
                    message_placeholder.markdown(buffer + " ")

        st.session_state.messages.append(
            {"role": "assistant", "content": buffer.strip()}
        )
