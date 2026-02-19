from fastapi import APIRouter
import pandas as pd

router = APIRouter(prefix="/api")

# eg: http://http://127.0.0.1:8000/api/price?code=sh.600004
@router.get("/price")
def get_price(code: str):
    df = pd.read_csv(f"./data/price_data/{code}.csv")
    return df.to_dict(orient="records")

