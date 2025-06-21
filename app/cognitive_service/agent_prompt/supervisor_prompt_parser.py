from typing import Literal

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel

from app.cognitive_service.agent_llm.llm_models import precise_llm_nano
from shared.datetime_util import get_kst_timestamp_label, get_kst_year_month_date_label


class SupervisorOutput(BaseModel):
    intent: Literal["tavel_conversation", "search"]
    travel_place: str
    travel_schedule: str
    travel_style: str

intent_parser = PydanticOutputParser(pydantic_object=SupervisorOutput)


supervisor_prompt = PromptTemplate.from_template("""
너는 사용자의 지시를 읽고 의도와 필요한 정보를 분석하는 여행 컨설턴트 KEA야.
KEA는 여행과 관련된 사용자의 대화를 분석하고 적절한 의도와 필요한 정보를 추출해.
여행 스케줄은 {today}를 기준으로 정리해.

<intents>
1. tavel_conversation 
- 사용자의 평범한 여행과 관련 대화 및 질문

2. search
- 사용자가 여행 도시 혹은 장소에 대한 추천 및 검색을 지시한 경우
</intents>

KEA는 의도와 함께 대화에서 아래의 정보를 같이 추출해
1. travel_place: 여행 도시 및 장소
2. travel_schedule: 여행 스케줄(YYYY-MM-DD)~(YYYY-MM-DD)
3. travel_style: 여행 스타일

반드시 JSON으로 응답합니다. 
JSON 형식:
{format_instructions}

사용자 메시지: {user_query}
""").partial(format_instructions=intent_parser.get_format_instructions())


def run_supervisor(user_input: str):
    formatted_prompt = supervisor_prompt.format(user_query=user_input, today=get_kst_year_month_date_label())
    raw_output = precise_llm_nano.invoke(formatted_prompt)

    print(f"🧾 전송한 프롬프트 정보: {formatted_prompt}\n원본 LLM 응답:\n {raw_output.content}")
    parsed = intent_parser.parse(raw_output.content)

    print("\n✅ 파싱된 JSON:")
    print(parsed.model_dump_json(indent=2))
    return parsed

# ✅ 6. Main 함수
if __name__ == "__main__":
    # user_input = "7월에 여자친구랑 오사카로 3박 4일 여행 가려고 해. 맛집 위주로 여행하고 싶어."
    test_user_input = "너는 뭐하는 애니?"
    run_supervisor(test_user_input)

