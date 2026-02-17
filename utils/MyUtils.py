import baostock as bs
import pandas as pd
import matplotlib.pyplot as plt

def get_stock_info(save_path="./stock_info.csv"):
    """获取所有股票代码数据"""
    try:
        # 登录系统
        bs.login()

        # 获取证券基本资料
        rs = bs.query_stock_basic()

        # 获取具体数据
        data_list = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())

        # 转换为DataFrame
        result = pd.DataFrame(data_list, columns=rs.fields)
        result = result[result['type'] == "1"]
        result = result[result["code_name"].apply(lambda x: "ST" not in x)]   # 去除ST的股票
        result = result[result["outDate"].apply(lambda x: x == "")]

        result = result[["code", "code_name", "ipoDate", "type", "status"]]

        result.to_csv(save_path, index=False, encoding="utf-8-sig")

        print(f"获取到股票数量: {len(result)}")
        print("\n股票列表:")
        print(result.head(10))

        # 登出系统
        bs.logout()

        return result
    except Exception as e:
        print(f"获取股票列表失败: {e}")
        return None


def get_stock_baostock(stock_code="sh.600000", start_date="2026-01-05", end_date="2026-03-01"):
    """
    - date：交易日期
    - code：证券代码
    - open：开盘价
    - high：最高价
    - low：最低价
    - close：收盘价
    - preclose：前一交易日收盘价
    - volume：成交量
    - amount：成交额
    - adjustflag：复权标记，1：后复权；2：前复权；3: 不复权
    - turn：换手率
    - tradestatus：交易状态，交易状态(1：正常交易 0：停牌）
    - pctChg：涨跌幅
    - isST：是否 ST 股票，是否ST股，1是，0否
    """

    fields = "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST"
    rs = bs.query_history_k_data_plus(stock_code,
                                      fields=fields,
                                      start_date=start_date, end_date=end_date,
                                      frequency="d", adjustflag="2")      # 前复权数据
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)

    return result


def plot_kline(df, title="K Line"):
    """
    画股票K线图

    参数
    ----------
    df : DataFrame
        必须包含 ['date','open','high','low','close']
    """

    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    df.reset_index(drop=True, inplace=True)

    fig, ax = plt.subplots(figsize=(12, 6))

    for i in range(len(df)):
        open_price = df.loc[i, 'open']
        close_price = df.loc[i, 'close']
        high = df.loc[i, 'high']
        low = df.loc[i, 'low']

        # 判断涨跌
        color = 'red' if close_price >= open_price else 'green'

        # 影线
        ax.plot([i, i], [low, high], color='black')

        # 实体
        ax.add_patch(
            plt.Rectangle(
                (i - 0.3, min(open_price, close_price)),
                0.6,
                abs(close_price - open_price),
                color=color
            )
        )

    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.grid(True)

    # x轴日期
    ax.set_xticks(range(0, len(df), max(len(df) // 10, 1)))
    ax.set_xticklabels(df['date'].dt.strftime('%m-%d')[::max(len(df) // 10, 1)])

    plt.tight_layout()
    plt.show()

def get_ma_data(df, price_col="close"):
    """计算均线数据"""
    df = df.copy()
    df["ma5"] = df[price_col].rolling(window=5).mean().round(2)
    df["ma10"] = df[price_col].rolling(window=10).mean().round(2)
    df["ma20"] = df[price_col].rolling(window=20).mean().round(2)
    df["ma30"] = df[price_col].rolling(window=30).mean().round(2)
    df["ma60"] = df[price_col].rolling(window=60).mean().round(2)
    return df

def get_kdj_data(df, n=9, k_period=3, d_period=3):
    df = df.copy()

    # RSV
    low_n = df['low'].rolling(n).min()
    high_n = df['high'].rolling(n).max()
    rsv = (df['close'] - low_n) / (high_n - low_n) * 100

    df['K'] = rsv.ewm(com=k_period - 1, adjust=False).mean()
    df['D'] = df['K'].ewm(com=d_period - 1, adjust=False).mean()
    df['J'] = 3 * df['K'] - 2 * df['D']

    return df

def get_macd_data(df, fast=12, slow=26, signal=9):
    df = df.copy()

    ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['close'].ewm(span=slow, adjust=False).mean()

    df['DIFF'] = ema_fast - ema_slow          # 快线
    df['DEA'] = df['DIFF'].ewm(span=signal, adjust=False).mean()  # 慢线
    df['MACD'] = df['DIFF'] - df['DEA']     # 快慢线之差

    return df


if __name__ == '__main__':
    data = get_stock_baostock("sh.600004", start_date="2024-01-01", end_date="2024-01-30")
    print(data)