import json
import textwrap
from dataclasses import dataclass

from shared.event_constant import SSETag


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
    event_type = event.get("event")
    node_name = event.get("name")
    data = event.get("data", {})

    match event_type:
        case ChainEvents.START:
            # print(f"[🚀 체인 시작] 노드 이름: {node_name}", flush=True)
            # sse_data["message"] = f"체인 시작: {node_name}"
            yield format_sse_event_state_json(tag_name=SSETag.NODE, event_type=ChainEvents.START, name=node_name, status="시작")

        case ChainEvents.STREAM:
            # print(f"[🔄 체인 중간 상태 스트리밍...] 노드 이름: {node_name}", flush=True)
            # sse_data["message"] = f"체인 중간 상태 스트리밍: {node_name}"
            yield format_sse_event_state_json(tag_name=SSETag.NODE, event_type=ChainEvents.STREAM, name=node_name, status="스트리밍")


        case ChainEvents.END:
            # print(f"[✅ 체인 종료] 노드 이름 : {node_name}", flush=True)
            # output = data.get("output")
            # print(f"[📦 최종 출력 결과] 노드 이름: {output}", flush=True)

            # yield format_sse_event_state(tag_name=SSE_NODE_TAG, event_type=ChainEvents.END, name=node_name, status="완료")
            yield format_sse_event_state_json(tag_name=SSETag.NODE, event_type=ChainEvents.END, name=node_name, status="완료")


        case ChatModelEvents.START:
            pass
            # print(f"[🧠 Chat 모델 시작] 노드 이름: {node_name}")
            # yield f"{SSE_NODE_TAG}### ChatModelEvents.START \n - 노드 정보: {node_name}\n - 상태: 시작\n\n\n\n"

        case ChatModelEvents.STREAM:
            chunk = data.get("chunk", {}).content
            # print(f"{chunk}", end="\n", flush=True)
            yield f"{SSETag.DATA}{chunk}\n\n"

        case ChatModelEvents.END:
            print(f"[🧠 Chat 모델 응답 완료] 노드 이름: {node_name}", flush=True)

            output = getattr(data.get("output", None), "content", "[출력 없음]")
            messages = data.get("input", {}).get("messages", [])
            if messages and isinstance(messages[0], list):
                user_message = messages[0][0].content
            else:
                user_message = "[메시지 없음]"

            print("\n", f"[💬 대화 요약]")
            print(f"🙋 대화 정보들: 현재 메시지 길이: {len(messages[0])} 정보: {messages}")
            print(f"🙋 사용자: {user_message}")
            print(f"🤖 응답: {output}", "\n")
            yield f"{SSETag.DATA} __DONE__\n\n"


        case LLMEvents.START:
            print(f"[📝 LLM 시작] 노드 이름: {node_name}", flush=True)

        case LLMEvents.STREAM:
            token = data.get("chunk", {}).get("text", "")
            print(f"{token}", flush=True)

        case LLMEvents.END:
            print(f"[📝 LLM 종료] 노드 이름: {node_name}", flush=True)

        case ToolEvents.START:
            tool_name = data.get('input')
            print(f"[🔧 툴 시작] 노드 이름: {node_name} 입력 정보: → {tool_name}", flush=True)
            # yield format_sse_event_state(tag_name=SSE_NODE_TAG, event_type=ToolEvents.START, name=tool_name,status="시작")
            yield format_sse_event_state_json(tag_name=SSETag.TOOL, event_type=ToolEvents.START, name=tool_name, status="시작")


        case ToolEvents.END:
            tool_output = data.get('output')
            print(f"[🔧 툴 종료] 노드 이름: {node_name} → 결과 정보:: {tool_output}", flush=True)
            # yield format_sse_event_state(tag_name=SSE_NODE_TAG, event_type=ToolEvents.END, name=tool_name, status="완료")
            yield format_sse_event_state_json(tag_name=SSETag.TOOL, event_type=ToolEvents.END, name=tool_output, status="완료")


        case RetrieverEvents.START:
            print(f"[🔍 리트리버 시작] 노드 이름: {node_name}", flush=True)
            # yield f"{SSE_SEARCH_TAG}### RetrieverEvents.START 노드 정보: {node_name} \n - 상태: 시작\n\n\n\n"
            yield format_sse_event_state_json(tag_name=SSETag.NODE, event_type=RetrieverEvents.START, name=node_name, status="시작")


        case RetrieverEvents.END:
            doc_list = data.get('documents', [])
            print(f"[🔍 리트리버 종료] 노드 이름: {node_name} → 문서 목록 정보: {doc_list}", flush=True)
            # yield f"{SSE_SEARCH_TAG}### RetrieverEvents.END 노드 정보: {node_name} 검색 호출 완료 문서 목록 : {doc_list}!\n\n\n\n"


        case PromptEvents.START:
            print(f"[🧱 프롬프트 시작] 노드 이름: {node_name}", flush=True)

        case PromptEvents.END:
            print(f"[🧱 프롬프트 완료] 노드 이름: {node_name}", flush=True)
            print(f"[📜 Prompt 텍스트] 노드 이름:\n{data.get('output')}", flush=True)

        case _:
            print(f"[📎 등록되지 않은 기타 이벤트] 이벤트 정보: {event_type} 노드 정보: {node_name}", flush=True)


def _sse_json(sse_data):
    return json.dumps(sse_data, ensure_ascii=False)

def format_sse_event_state(tag_name: str, event_type: str, name: str, status: str) -> str:
    """
    SSE 마크다운 메시지 생성기.
    """
    return textwrap.dedent(f"""{tag_name} ### {event_type}  
                            - 정보: `{name}`  
                            - 상태: {status}""")

def format_sse_event_state_json(tag_name: str, event_type: str, name: str, status: str) -> str:
    payload = {
        "event_type": event_type,
        "name": name,
        "status": status
    }
    return f"{tag_name} {json.dumps(payload, ensure_ascii=False)}\n\n"