from datetime import date
from typing import List

from app.cognitive_service.agent_tool.calendar_tool import TravelPlansInput
from app.models.travel_plan import TravelPlan


def format_user_messages_with_index(messages):
    return "\n".join(f"{idx + 1}. {msg}" for idx, msg in enumerate(messages))


def to_html_format(html_body):
    html_content = f"""<!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>여행 계획 공유</title>
    </head>
    <body>
    {html_body}
    </body>
    </html>
    """
    return html_content



def convert_input_to_travel_plans(inputs: TravelPlansInput) -> tuple[str, List[TravelPlan]]:
    if not inputs:
        raise ValueError("입력 일정 정보가 비어 있습니다.")

    session_id = inputs.session_id
    travel_plans = [
        TravelPlan(
            session_id=session_id,
            trip_date=plan.trip_date,
            trip_schedule=plan.trip_schedule,
            created_at=date.today().isoformat()
        )
        for plan in inputs.plans
    ]
    return session_id, travel_plans