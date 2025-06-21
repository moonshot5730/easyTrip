import textwrap

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import PromptTemplate

from app.cognitive_service.agent_core.graph_state import AgentState, get_last_message
from app.cognitive_service.agent_llm.llm_models import creative_llm_nano, precise_llm_mini, precise_llm_nano
from app.cognitive_service.agent_tool.travel_search_tool import place_search_tool
from app.core.logger.logger_config import api_logger
from shared.datetime_util import get_kst_year_month_date_label


travel_search_system_prompt_template = textwrap.dedent("""
    당신은 대한민국 여행 장소 및 도시를 검색해주는 AI 리서치 KET입니다.
    
    KET의 도구 사용 규칙:
    - 사용자 질문이 웹 검색 혹은 검색을 요구한 경우 웹 검색 도구 'tavily_web_search'을 사용하세요.
    - 사용자가 단순하게 여행 지역 및 장소를 추천 혹은 제안한 경우 여행 지역과 장소를 제안하세요.
    
    사용 가능한 도구:
    - tavily_web_search: 대한민국 여행지를 주제로 검색어를 전달해 웹 검색을 수행합니다.
    
    사용자 질문: {user_query}
    """)


def travel_search_conversation(state: AgentState):
    api_logger.info(f"[travel_search_conversation!!!] 현재 상태 정보입니다: {state.get("messages", [])}")

    user_query = state.get("user_query") or get_last_message(messages=state.get("messages", []))
    new_user_message = HumanMessage(content=user_query)

    system_message = SystemMessage(content=PromptTemplate.from_template(travel_search_system_prompt_template).format(user_query=user_query))
    messages = [system_message] + [new_user_message]

    api_logger.info(f"[travel_search_conversation] messages : {messages}")

    llm_response = precise_llm_nano.bind_tools([place_search_tool]).invoke(messages)
    api_logger.info(f"[travel_search_conversation] 응답 : {llm_response.content}")

    tool_calls = getattr(llm_response, "tool_calls", None)

    results = []
    if tool_calls:
        for tool_call in tool_calls:
            if tool_call["name"] == "tavily_web_search":
                args = tool_call["args"]
                tool_result = place_search_tool.invoke(args)
                results.append(tool_result)

        api_logger.info(f"[웹 검색 결과!! ] {results}")

    return {
        "messages": state.get("messages", []) + [new_user_message, AIMessage(content=llm_response.content)]
    }


if __name__ == '__main__':
    messages = [
        SystemMessage(content=travel_search_system_prompt_template),
        HumanMessage(content="대한민국 강원도 여행지에 대해서 검색해주세요.")
    ]

    binding_llm = precise_llm_nano.bind_tools([place_search_tool])
    llm_response = binding_llm.invoke(messages)

    # 📌 function call이 발생했는지 확인
    tool_calls = getattr(llm_response, "tool_calls", None)

    results = []
    if tool_calls:
        for tool_call in tool_calls:
            if tool_call["name"] == "tavily_web_search":
                args = tool_call["args"]
                tool_result = place_search_tool.invoke(args)
                results.append(tool_result)

    print(f"llm 응답 {llm_response}")
    print(f"tool_calls 정보: {tool_calls}")
    print(f"검색 결과 : {results}")