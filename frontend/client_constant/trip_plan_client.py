from typing import List, Dict, Generator

import requests
from requests import RequestException


def get_streaming_response(messages: List[Dict[str, str]], api_url: str) -> Generator[str, None, None]:
    """
    백엔드 SSE API로 메시지를 전송하고, 스트리밍 응답을 chunk 단위로 반환합니다.

    Args:
        messages (List[Dict[str, str]]): 채팅 기록 리스트.
        api_url (str): 요청을 보낼 SSE API의 전체 주소.

    Yields:
        Generator[str, None, None]: 'data: ' 접두사가 제거된 응답 chunk.
    """
    try:
        with requests.post(
                api_url,
                json={"messages": messages},
                stream=True,
                headers={"Accept": "text/event-stream"},
        ) as resp:
            # HTTP 오류 발생 시 예외 처리
            resp.raise_for_status()

            for line in resp.iter_lines(decode_unicode=True):
                if line and line.startswith("data: "):
                    yield line.removeprefix("data: ")

    except RequestException as e:
        error_message = f"**[오류]** 백엔드 서버에 연결할 수 없습니다: {e}"
        print(error_message)  # 로깅
        yield error_message