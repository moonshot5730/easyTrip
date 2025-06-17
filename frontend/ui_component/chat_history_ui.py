from typing import Dict, List

import streamlit as st


def render_chat_history(messages: List[Dict[str, str]]):
    """
    세션 상태에 저장된 메시지를 순회하며 채팅 UI를 렌더링합니다.
    """
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
