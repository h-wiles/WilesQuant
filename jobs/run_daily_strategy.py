from utils.MyUtils import get_ma_data
import pandas as pd

def ma_diverge_policy():
    """找出和5日线偏离5%以上并小于5%的股票，当天尾盘收盘价买入，止盈：2%，止损：1%"""
    stock_info = pd.read_csv("./data/stock_info.csv")
    stock_info = stock_info[stock_info["code"].apply(lambda x: not x.startswith(("sh.68", "sz.30")))]    #去掉科创板
    stock_codes = stock_info["code"].tolist()
    stock_names = stock_info["code_name"].tolist()

    results = []
    for code, name in zip(stock_codes, stock_names):
        df = pd.read_csv("./data/price_data/" + code + ".csv")

        df = get_ma_data(df)
        df = df.dropna(subset=["ma5"])

        today_df = df.tail(1)
        if len(today_df)>0:     # 防止新股存在没有
            date = today_df["date"].iloc[0]
            ma5 = today_df["ma5"].iloc[0]
            close = today_df["close"].iloc[0]
            premium_rate = (ma5 - close)/ma5

            if premium_rate > 0.05:
                results.append({"date":date , "code": code, "name":name, "close":close, "ma5":ma5, "premium_rate": premium_rate})

    return results