from datetime import date
from typing import List

from app.models.travel_plan import TravelPlan
from app.schemes.calendar_scheme import TravelPlanInput


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



def convert_input_to_travel_plans(session_id: str, inputs: List[TravelPlanInput]) -> list[TravelPlan]:
    if not inputs:
        raise ValueError("입력 일정 정보가 비어 있습니다.")

    travel_plans = [
        TravelPlan(
            session_id=session_id,
            trip_date=plan_input.trip_date,
            trip_schedule=plan_input.trip_schedule,
            created_at=date.today().isoformat()
        )
        for plan_input in inputs
    ]
    return travel_plans