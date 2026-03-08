from fastapi import APIRouter
from main_agents import get_agent_response

router = APIRouter(prefix="/api")
# eg: http://127.0.0.1:8000/api/ai_analysis?code=sh.600004&trade_date=2026-03-06
@router.get("/ai_analysis")
def get_backtest(code: str, trade_date: str):
    state, _ = get_agent_response(code, trade_date)
    return state