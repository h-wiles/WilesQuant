import pandas as pd
from wiles_agents.graph.trading_graph import TradingAgentsGraph
from wiles_agents.default_config import DEFAULT_CONFIG
from dotenv import load_dotenv
from datetime import datetime
import os
import warnings
import akshare as ak
from collections import defaultdict
from utils.MyUtils import get_stock_name
warnings.filterwarnings("ignore")


def date_normalize(trade_date: str) -> str:
    # norm the trade date
    try:
        trade_calendar = pd.read_csv("./data/trade_calendar.csv")
    except FileNotFoundError:
        trade_calendar = ak.tool_trade_date_hist_sina()
    trade_calendar["trade_date"] = pd.to_datetime(trade_calendar["trade_date"])
    today = datetime.today().strftime("%Y-%m-%d")
    calendar = trade_calendar[(trade_calendar["trade_date"] <= pd.to_datetime(trade_date)) & (
                trade_calendar["trade_date"] <= pd.to_datetime(today))]
    date = str(calendar["trade_date"].iloc[-1])[:10]
    return date


def get_agent_response(code, trade_date):
    load_dotenv("./.env")

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

    types = ['market_report', 'news_report', 'fundamentals_report', 'investment_debate_state', 'investment_plan',
              'trader_investment_plan', 'risk_debate_state', 'final_trade_decision']
    dir_path = os.path.join("data", "agent_response", code, trade_date)
    os.makedirs(dir_path, exist_ok=True)
    files = os.listdir(dir_path)

    if os.path.exists(dir_path) and all(any(f.startswith(prefix) for f in files)for prefix in types):
        state = defaultdict(str)
        for k in types:
            with open(os.path.join(dir_path, f"{k}.md"), "r") as f:
                tmp_md = f.read()
            state[k] = tmp_md
        decision = state["final_trade_decision"]
    else:
        # Initialize with custom config
        ta = TradingAgentsGraph(debug=True, config=config)

        state, decision = ta.propagate(code, trade_date)

        # Memorize mistakes and reflect
        # ta.reflect_and_remember(1000) # parameter is the position returns
        for k in types:
            file_path = os.path.join(dir_path, f"{k}.md")
            with open(file_path, "w") as f:
                f.write(str(state[k]))
    return state, decision

def main_agents(code, trade_date):
    # os.environ["http_proxy"] = "http://127.0.0.1:7890"
    # os.environ["https_proxy"] = "http://127.0.0.1:7890"
    os.environ["HTTP_PROXY"] = ""
    os.environ["HTTPS_PROXY"] = ""

    trade_date = date_normalize(trade_date)
    state, decision= get_agent_response(code, trade_date)
    state["stock_name"] = get_stock_name(code)
    state["code"] = code
    return state, decision
