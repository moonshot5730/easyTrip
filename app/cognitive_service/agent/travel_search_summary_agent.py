import asyncio
import textwrap

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate

from app.cognitive_service.agent_core.graph_state import AgentState
from app.cognitive_service.agent_llm.llm_models import precise_llm_nano
from app.cognitive_service.agent_tool.travel_search_tool import \
    place_search_tool
from app.core.logger.logger_config import api_logger
from app.external.openai.openai_client import precise_openai_fallbacks
from shared.datetime_util import get_kst_year_month_date_label

travel_search_summary_system_prompt_template = textwrap.dedent(
    """
    당신은 웹으로 검색된 정보들을 마크다운으로 요약 정리해주는 글쓰기 전문가 KET입니다.
    KET는 웹 검색으로 정리된 여행 관련 결과 정보들을 전달받습니다.
    검색한 날짜는 {today}입니다. 
    
    KET의 응답 스타일:
    - 검색된 결과를 정리했다고 안내합니다.
    - 정보가 너무 많은 경우 반복되고, 강조되는 정보 3~5개로 정리합니다.
    - URL 링크 정보를 쉽게 확인할 수 있도록 마크다운으로 표시해줍니다.
    ** 별도로 참조한 링크를 정리합니다.
    
    웹 검색 결과 정보 : {search_results}
    """
)


def travel_search_summary_conversation(state: AgentState):
    """
    검색된 결과를 기반으로 마크다운 요약 응답을 내려줍니다.
    :param state: 그래프 스테이트 정보
    :return: 검색 결과를 요약해서 내려줍니다. [이벤트에서 처리]
    """
    api_logger.info(
        f"[travel_search_summary_conversation!!!] 현재 상태 정보입니다: {state.get("messages", [])}"
    )

    system_message = SystemMessage(
        content=PromptTemplate.from_template(
            travel_search_summary_system_prompt_template
        ).format(
            search_results=state.get("websearch_results", []),
            today=get_kst_year_month_date_label(),
        )
    )
    llm_response = precise_openai_fallbacks.invoke([system_message])

    return {
        "messages": state.get("messages", [])
        + [AIMessage(content=llm_response.content)],
        "is_websearh": False,
    }



if __name__ == "__main__":
    async def run_test():
        test_state: AgentState = {
            "user_name": "문현준",
            "websearch_results": textwrap.dedent("""
                1. 강릉 안목해변은 여름철 해수욕과 카페거리로 유명합니다.
                2. 경포대는 아름다운 호수와 해변 경관으로 여행객들에게 인기가 높습니다.
                3. 오죽헌은 율곡 이이와 신사임당의 유적으로 조용한 분위기의 명소입니다.
                """),
            "messages": [],
        }

        result = travel_search_summary_conversation(test_state)

        print("\n📝 요약 응답:")
        for msg in result["messages"]:
            print(f"{msg}")

    asyncio.run(run_test())