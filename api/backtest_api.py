from fastapi import APIRouter
from backtest.backtest import main_backtest

router = APIRouter(prefix="/api")

# eg: http://127.0.0.1:8000/api/backtest?code=sh.600004&strategy=ma5 diverge
@router.get("/backtest")
def get_backtest(code: str, entry_strategy: str, exit_strategy: str):
    df = main_backtest(code, entry_strategy, exit_strategy, plot_equity_curve=False)
    return df.to_dict(orient="records")