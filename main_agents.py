import pandas as pd

from wiles_agents.graph.trading_graph import TradingAgentsGraph
from wiles_agents.default_config import DEFAULT_CONFIG
from dotenv import load_dotenv
from datetime import datetime
import os
import warnings
import akshare as ak
warnings.filterwarnings("ignore")

# Load environment variables from .env file
load_dotenv("../.env")
config = DEFAULT_CONFIG
# os.environ["http_proxy"] = "http://127.0.0.1:7890"
# os.environ["https_proxy"] = "http://127.0.0.1:7890"
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""

# Create a custom config
config = DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "deepseek-chat"  # Use a different model
config["quick_think_llm"] = "deepseek-chat"  # Use a different model
config["max_debate_rounds"] = 1  # Increase debate rounds

# Configure data vendors (default uses yfinance and alpha_vantage)
config["data_vendors"] = {
    "core_stock_apis": "local",           # Options: yfinance, alpha_vantage, local
    "technical_indicators": "local",      # Options: yfinance, alpha_vantage, local
    "fundamental_data": "baostock",     # Options: openai, alpha_vantage, local
    "news_data": "akshare",            # Options: openai, alpha_vantage, google, local
}

# Initialize with custom config
ta = TradingAgentsGraph(debug=True, config=config)

# 日期处理，若输入未来日期，则自动替换成近一个交易日
code, trade_date = "sh.600004", "2026-06-15"
trade_calendar = ak.tool_trade_date_hist_sina()
trade_calendar["trade_date"] = pd.to_datetime(trade_calendar["trade_date"])
today = datetime.today().strftime("%Y-%m-%d")
calendar = trade_calendar[(trade_calendar["trade_date"]<=pd.to_datetime(trade_date)) & (trade_calendar["trade_date"]<=pd.to_datetime(today))]
trade_date = str(calendar["trade_date"].iloc[-1])[:10]

# forward propagate
state, decision = ta.propagate(code, trade_date)
print(decision)

# Memorize mistakes and reflect
# ta.reflect_and_remember(1000) # parameter is the position returns
