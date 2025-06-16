from langchain_core.tools import Tool


def search_travel_info(query: str) -> str:
    return f"'{query}'에 대한 여행 정보를 찾아봅니다."

tools = [
    Tool.from_function(
        func=search_travel_info,
        name="SearchTravelInfo",
        description="여행 정보를 검색해주는 도구입니다."
    )
]

