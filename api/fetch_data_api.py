from fastapi import APIRouter
from jobs.get_data_day import get_data_day

router = APIRouter(prefix="/api")

# eg: http://127.0.0.1:8000/api/get_data_day
@router.get("/get_data_day")
def fetch_data(code):
    message = get_data_day(code, basic_data_path="./data/price_data")
    return message