import os
from pprint import pprint

from langchain_tavily import TavilySearch

os.environ["TAVILY_API_KEY"] = "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"

place_search_tool = TavilySearch(
    name="tavily_web_search", # 툴 이름
    max_results=3,
    topic="general",
)


def parse_tavily_results_markdown(tool_result: dict) -> str:
    if not tool_result or "results" not in tool_result:
        return "🔍 검색 결과가 없습니다."

    result_lines = [f"## {tool_result["query"]} Tavily 검색 결과입니다."]
    for idx, item in enumerate(tool_result["results"], start=1):

        title = item.get("title", "제목 없음")
        url = item.get("url", "#")
        summary = item.get("content", "")
        result_lines.append(f"**{idx}. [{title}]({url})**\n\n-요약 정보: {summary.strip()}\n")

    return "\n---\n".join(result_lines)

if __name__ == '__main__':
    query = "시원한 여름 휴가 및 대한민국 여행지"

    # Tavily 웹 검색
    response = place_search_tool.invoke(input=query)
    pprint(response)
