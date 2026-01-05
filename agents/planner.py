from agents.planner_agent import generate_daily_plan
from datetime import datetime
from zoneinfo import ZoneInfo

def get_today_plan():
    """
    Public planner interface.
    Called by:
    - FastAPI
    - Streamlit UI
    - Background jobs (later)
    """

    tz = ZoneInfo("Asia/Kolkata")
    generated_at = datetime.now(tz).isoformat()

    plan = generate_daily_plan()

    return {
        "date": generated_at,
        "planner_type": "daily_interview_prep",
        "plan": plan
    }

