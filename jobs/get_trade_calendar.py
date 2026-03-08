import pandas as pd
import os
import warnings
import akshare as ak
warnings.filterwarnings("ignore")

os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""

trade_calendar = ak.tool_trade_date_hist_sina()
trade_calendar["trade_date"] = pd.to_datetime(trade_calendar["trade_date"])
trade_calendar.to_csv("./data/trade_calendar.csv", index=False)