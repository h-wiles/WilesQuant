from utils.MyUtils import get_stock_baostock
from datetime import datetime, timedelta
import baostock as bs
from tqdm import tqdm
import pandas as pd
import os
import logging
import warnings
warnings.filterwarnings("ignore")
logging.basicConfig(filename="../logs/get_data.log", level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', encoding="utf-8")
logger = logging.getLogger()


def get_basic_data():
    bs.login()
    logger.info("=================get_basic_data=====================")
    today = datetime.today()
    past_day = today - timedelta(days=2000)
    start_date, end_date = str(past_day)[:10], str(today)[:10]
    logger.info(f"begin basic data generate: start_date {start_date}, end_date {end_date}, time now {today}")

    root_path = os.path.abspath('..')
    root_path = os.path.join(root_path, f'data/price_data')
    if not os.path.exists(root_path):
        os.mkdir(root_path)

    stock_info = pd.read_csv("../data/stock_info.csv")
    stock_codes = stock_info["code"].tolist()
    stock_codes = [code for code in stock_codes if not (code.startswith(("sh.68", "sz.30")))]   # 去掉创业板和科创板
    try:
        for code in tqdm(stock_codes, desc="get basic data"):
            df = get_stock_baostock(code, start_date=start_date, end_date=end_date)

            df.to_csv(f"{root_path}/{code}.csv", index=False)
        logger.info(f"basic data generate success, total codes: {len(stock_codes)}")
    except Exception as e:
        logger.error("basic data generate fail, error: ", e)
    bs.logout()


def update_data(basic_data_path = "../data/price_data"):
    bs.login()
    logger.info("==================update_data=======================")
    today = datetime.today()
    stock_info = pd.read_csv("../data/stock_info.csv")
    stock_codes = stock_info["code"].tolist()
    stock_codes = [code for code in stock_codes if not (code.startswith(("sh.68", "sz.30")))]  # 去掉创业板和科创板
    logger.info(f"begin data update: time now {today}")

    insert_n = 0
    try:
        for code in tqdm(stock_codes, desc="update data"):
            file_path = os.path.join(basic_data_path, f"{code}.csv")
            basic_data = pd.read_csv(file_path)

            start_date = basic_data.sort_values(by=["date"], ascending=False).iloc[0]["date"]
            start_date = pd.to_datetime(start_date) + pd.Timedelta(days=1)
            start_date = str(start_date)[:10]
            end_date = str(today)[:10]

            new_data = get_stock_baostock(code, start_date, end_date)
            insert_n += len(new_data)

            data = pd.concat([basic_data, new_data], axis=0, ignore_index=True)
            data.to_csv(f"{basic_data_path}/{code}.csv", index=False)
        logger.info(f"update data success, total update number: {insert_n}, total codes: {len(stock_codes)}")
    except Exception as e:
        logger.error("update data fail, error: ", e)

    bs.logout()


# 每天19:00执行数据更新,使用工具：crontab，用crontab -e查看
if __name__ == '__main__':
    # 如果基础数据存在
    if os.path.exists("../data/price_data") and os.listdir(os.path.abspath("../data/price_data")):
        update_data(basic_data_path = "../data/price_data")
    # 如果基础数据不存在
    else:
        get_basic_data()