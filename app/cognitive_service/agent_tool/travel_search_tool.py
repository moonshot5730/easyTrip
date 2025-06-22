import os
from pprint import pprint

from langchain_core.messages import AIMessage
from langchain_tavily import TavilySearch

from shared.format_util import format_user_messages_with_index

os.environ["TAVILY_API_KEY"] = "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"

place_search_tool = TavilySearch(
    name="tavily_web_search",  # 툴 이름
    max_results=3,
    topic="general",
)


def get_web_search_results(llm_response):
    tool_calls = getattr(llm_response, "tool_calls", None)
    tool_messages = []
    if tool_calls:
        for tool_call in tool_calls:
            if tool_call["name"] == "tavily_web_search":
                args = tool_call["args"]
                tool_result = place_search_tool.invoke(args)

                tool_content = parse_tavily_results(tool_result)
                tool_messages.append(AIMessage(content=tool_content))
    return tool_messages


def parse_tavily_results_markdown(tool_result: dict) -> str:
    if not tool_result or "results" not in tool_result:
        return "🔍 검색 결과가 없습니다."

    result_lines = [f"#### '{tool_result["query"]}' 키워드 검색 결과"]
    for idx, item in enumerate(tool_result["results"], start=1):

        title = item.get("title", "제목 없음")
        url = item.get("url", "#")
        result_lines.append(f"**{idx}. [{title}]({url})**\n")

    return "\n".join(result_lines) + "\n---\n"


def parse_tavily_results(tool_result: dict) -> str:
    if not tool_result or "results" not in tool_result:
        return "검색 결과가 없습니다."

    result_lines = []
    for idx, item in enumerate(tool_result["results"], start=1):
        summary = item.get("content", "")
        result_lines.append(summary.strip())

    return format_user_messages_with_index(result_lines)


if __name__ == "__main__":
    query = "시원한 여름 휴가 및 대한민국 여행지"

    # Tavily 웹 검색
    response = place_search_tool.invoke(input=query)
    pprint(response)
