from langchain_core.tools import tool


@tool
def search_place_tool(user_query: str) -> dict:
    """
    사용자의 요청에 따라 추천 여행지를 반환합니다.
    실제 구현에서는 외부 API나 벡터 검색을 연동할 수 있습니다.
    """
    # 여기는 하드코딩 예시 — 실제로는 LLM, 검색 API, 벡터 DB 등을 연동 가능
    recommendations = [
        "강릉 – 해변과 커피거리로 유명한 동해안 도시",
        "부산 – 바다와 도시가 함께 있는 대표 여행지",
        "전주 – 한옥마을과 맛집으로 유명한 문화 여행지",
        "제주 – 자연, 바다, 맛집이 있는 섬 여행지"
    ]

    return {
        "search_results": recommendations,
        "message": "추천 여행지를 몇 가지 찾아드렸어요! 관심 가는 곳이 있으신가요?"
    }