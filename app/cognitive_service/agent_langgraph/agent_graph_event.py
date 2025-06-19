import json
from dataclasses import dataclass

from app.core.logger.logger_config import get_logger
from shared.event_constant import SPLIT_PATTEN, DATA_TAG

logger = get_logger()

@dataclass(frozen=True)
class LLMEvents:
    START: str = "on_llm_start"
    STREAM: str = "on_llm_stream"
    END: str = "on_llm_end"

@dataclass(frozen=True)
class ChatModelEvents:
    START: str = "on_chat_model_start"
    STREAM: str = "on_chat_model_stream"
    END: str = "on_chat_model_end"

@dataclass(frozen=True)
class ChainEvents:
    START: str = "on_chain_start"
    STREAM: str = "on_chain_stream"
    END: str = "on_chain_end"

@dataclass(frozen=True)
class ToolEvents:
    START: str = "on_tool_start"
    END: str = "on_tool_end"

@dataclass(frozen=True)
class RetrieverEvents:
    START: str = "on_retriever_start"
    END: str = "on_retriever_end"

@dataclass(frozen=True)
class PromptEvents:
    START: str = "on_prompt_start"
    END: str = "on_prompt_end"


def handle_streaming_event(event: dict):
    logger.info(f"event 동작 하나? : {event}")

    event_type = event.get("event")
    node_name = event.get("name")
    data = event.get("data", {})

    sse_data = {
        "kind": event_type,
        "name": node_name,
        "content": None
    }

    if event_type == ChainEvents.START:
        print(f"[🚀 체인 시작] 노드 이름: {node_name}", flush=True)
        sse_data["message"] = f"체인 시작: {node_name}"

    elif event_type == ChainEvents.STREAM:
        print(f"[🔄 체인 중간 상태 스트리밍...] 노드 이름: {node_name}", flush=True)
        sse_data["message"] = f"체인 중간 상태 스트리밍: {node_name}"

    elif event_type == ChainEvents.END:
        print(f"[✅ 체인 종료] 노드 이름 : {node_name}", flush=True)
        output = data.get("output")
        print(f"[📦 최종 출력 결과] 노드 이름: {output}", flush=True)

    elif event_type == ChatModelEvents.START:
        print(f"[🧠 Chat 모델 시작] 노드 이름: {node_name}", flush=True)

    elif event_type == ChatModelEvents.STREAM:
        chunk = data.get("chunk", {}).content
        print(f"{repr(chunk)}", end="\n", flush=True)
        # yield 구문은 이 함수가 generator여야 작동함. 이건 처리 방식에 따라 따로 바꿔야 함.
        yield f"{DATA_TAG}{chunk}{SPLIT_PATTEN}"

    elif event_type == ChatModelEvents.END:
        print(f"[🧠 Chat 모델 종료] 노드 이름: {node_name}", flush=True)

    elif event_type == LLMEvents.START:
        print(f"[📝 LLM 시작] 노드 이름: {node_name}", flush=True)

    elif event_type == LLMEvents.STREAM:
        token = data.get("chunk", {}).get("text", "")
        print(f"{token}", flush=True)

    elif event_type == LLMEvents.END:
        print(f"[📝 LLM 종료] 노드 이름: {node_name}", flush=True)

    elif event_type == ToolEvents.START:
        print(f"[🔧 툴 시작] 노드 이름: {node_name} 입력 정보: → {data.get('input')}", flush=True)

    elif event_type == ToolEvents.END:
        print(f"[🔧 툴 종료] 노드 이름: {node_name} → 결과 정보:: {data.get('output')}", flush=True)

    elif event_type == RetrieverEvents.START:
        print(f"[🔍 리트리버 시작] 노드 이름: {node_name}", flush=True)

    elif event_type == RetrieverEvents.END:
        print(f"[🔍 리트리버 종료] 노드 이름: {node_name} → 문서 목록 정보: {len(data.get('documents', []))}", flush=True)

    elif event_type == PromptEvents.START:
        print(f"[🧱 프롬프트 시작] 노드 이름: {node_name}", flush=True)

    elif event_type == PromptEvents.END:
        print(f"[🧱 프롬프트 완료] 노드 이름: {node_name}", flush=True)
        print(f"[📜 Prompt 텍스트] 노드 이름:\n{data.get('output')}", flush=True)

    else:
        print(f"[📎 등록되지 않은 기타 이벤트] 이벤트 정보: {event_type} 노드 정보: {node_name}", flush=True)


def _sse_json(sse_data):
    return json.dumps(sse_data, ensure_ascii=False)