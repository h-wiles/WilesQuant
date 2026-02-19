from fastapi import FastAPI
from api.price_api import router as price_router
from api.backtest_api import router as backtest_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Quant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 开发阶段允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 注册接口
app.include_router(price_router)
app.include_router(backtest_router)
