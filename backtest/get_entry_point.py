import pandas as pd
from utils.MyUtils import get_ma_data, get_kdj_data, get_macd_data
import warnings
warnings.filterwarnings("ignore")

class EntryPoint:
    def __init__(self, code, signal_col="signal"):
        self.df = pd.read_csv(f"../data/price_data/{code}.csv")
        self.signal_col = signal_col
        self.df[signal_col] = 0

    def ma5_diverge_entry(self):
        """ma5 均线和价格偏离大于5%，且价格小于均价线，收盘价进场"""
        df = get_ma_data(self.df)
        df = df.dropna(subset=["ma5"])

        df["premium_rate"] = (df["ma5"] - df["close"]) / df["ma5"]
        df[self.signal_col] = df["premium_rate"].apply(lambda x: 1 if x>0.05 else 0)

        df = df.reset_index(drop=True)

        return df

    def kdj_oversold_entry(self):
        """kdj 超卖，J<0，收盘价进场"""
        df = get_kdj_data(self.df)
        df[self.signal_col] = df["J"].apply(lambda x: 1 if x<0 else 0)

        df = df.reset_index(drop=True)

        return df

    def macd_golden_cross_entry(self):
        """
        MACD金叉，收盘价进场
        条件：
        1. DIF 上穿 DEA（金叉）
        2. 金叉发生在 0 轴下方
        """

        df = get_macd_data(self.df)

        prev_macd = df['MACD'].shift(1)         # 前一天的值
        prev_signal = df['MACD_signal'].shift(1)

        golden_cross = (prev_macd < prev_signal) & (df['MACD'] > df['MACD_signal'])      # macd金叉

        below_zero = df['MACD'] < 0     # 在零轴下方
        df.loc[golden_cross & below_zero, self.signal_col] = 1

        return df

    def macd_bullish_divergence_entry(self, lookback=20, signal_col="signal"):
        """
        MACD底背离，收盘价进场
        price 创前20天新低 + MACD 未创新低
        """

        df = get_macd_data(self.df)

        # 最近N天最低价 & 最低MACD
        df['price_low_N'] = df['close'].rolling(lookback).min()
        df['macd_low_N'] = df['MACD'].rolling(lookback).min()

        price_new_low = df['close'] <= df['price_low_N'].shift(1)     # 价格是否创新低
        macd_not_new_low = df['MACD'] > df['macd_low_N'].shift(1)    # MACD是否没创新低

        df.loc[price_new_low & macd_not_new_low, signal_col] = 1      # 组合条件

        return df

    def volume_breakout_entry(self, signal_col="signal",
                              price_window=20, vol_window=5, vol_ratio=1.5):
        """
        放量突破阶段新高，收盘价进场：价格突破近期高点，成交量放大
        """
        df = self.df
        df[signal_col] = 0

        df['high_N'] = df['high'].rolling(price_window).max()       # 过去N日最高价
        df['vol_ma'] = df['volume'].rolling(vol_window).mean()       # 成交量均值

        price_breakout = df['close'] > df['high_N'].shift(1)       # 条件1：价格突破
        volume_expand = df['volume'] > df['vol_ma'] * vol_ratio       # 条件2：放量

        # 进场信号
        df.loc[price_breakout & volume_expand, signal_col] = 1

        return df


if __name__ == '__main__':
    ep = EntryPoint(code="sh.600004", signal_col="signal")
    res = ep.macd_golden_cross_entry()
    print(res)