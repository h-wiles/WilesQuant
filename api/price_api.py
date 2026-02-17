from fastapi import APIRouter
import pandas as pd

router = APIRouter(prefix="/api")

@router.get("/price")
def get_price(code: str):
    df = pd.read_csv(f"./data/price_data/{code}.csv")
    return df.to_dict(orient="records")
