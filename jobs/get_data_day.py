from collections import defaultdict

from utils.MyUtils import get_stock_baostock
from datetime import datetime, timedelta
import baostock as bs
from tqdm import tqdm
import pandas as pd
import os
import logging
import warnings
warnings.filterwarnings("ignore")
logging.basicConfig(filename="./logs/get_data.log", level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', encoding="utf-8")
logger = logging.getLogger()


def get_basic_data(code):
    logger.info("=================get_basic_data=====================")
    today = datetime.today()
    past_day = today - timedelta(days=2000)
    start_date, end_date = str(past_day)[:10], str(today)[:10]
    info_message = f"begin basic data generate: start_date {start_date}, end_date {end_date}, time now {today}"
    logger.info(info_message)

    df = pd.DataFrame()
    try:
        df = get_stock_baostock(code, start_date=start_date, end_date=end_date)
    except Exception as e:
        logger.error("basic data generate fail, error: ", e)

    return df


def update_data(code, basic_data_path = "../data/price_data"):
    logger.info("==================update_data=======================")
    today = datetime.today()  # 去掉创业板和科创板

    insert_n = 0
    file_path = os.path.join(basic_data_path, f"{code}.csv")
    try:
        basic_data = pd.read_csv(file_path)
        start_date = basic_data.sort_values(by=["date"], ascending=False).iloc[0]["date"]
        start_date = pd.to_datetime(start_date) + pd.Timedelta(days=1)
        start_date = str(start_date)[:10]
        end_date = str(today)[:10]

        new_data = get_stock_baostock(code, start_date, end_date)
        insert_n += len(new_data)

        df = pd.concat([basic_data, new_data], axis=0, ignore_index=True)
    except FileNotFoundError:
        df = get_basic_data(code)

    return df


def get_data_day(code, basic_data_path = "./data/price_data"):
    bs.login()
    stock_info = pd.read_csv("./data/stock_info.csv")
    stock_codes = stock_info["code"].tolist()
    stock_codes = [code for code in stock_codes if not (code.startswith(("sh.68", "sz.30")))]   # 去掉创业板和科创板
    if not os.path.exists(basic_data_path):
        os.mkdir(basic_data_path)
    message = defaultdict(str)
    if code + ".csv" not in os.listdir(basic_data_path):
        df = get_basic_data(code)
        message["message"] = "更新成功，基础数据不存在，全量更新"
    # 如果基础数据存在，执行更新操作
    else:
        df = update_data(code, basic_data_path=basic_data_path)
        message["message"] = "更新成功，基础数据存在，增量更新"
    df.to_csv(f"{basic_data_path}/{code}.csv", index=False)
    bs.logout()
    start_date = df["date"].iloc[0]
    end_date = df["date"].iloc[-1]
    message["start_date"] = start_date
    message["end_date"] = end_date
    message["code"] = code
    return message
