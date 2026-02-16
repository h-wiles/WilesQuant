import pandas as pd
from utils.MyUtils import get_ma_data
import warnings
warnings.filterwarnings("ignore")

class EntryPoint:
    def __init__(self, code, signal_col="signal"):
        df = pd.read_csv(f"../data/price_data/{code}.csv")
        self.df = df
        self.signal_col = signal_col

    def ma5_diverge_entry(self):
        """ma5 均线和价格偏离大于5%，且价格小于均价线，收盘价进场"""
        df = get_ma_data(self.df)
        df = df.dropna(subset=["ma5"])

        df["premium_rate"] = (df["ma5"] - df["close"]) / df["ma5"]
        df[self.signal_col] = df["premium_rate"].apply(lambda x: 1 if x>0.05 else 0)

        df = df.reset_index(drop=True)

        return df

    def kdj_oversold_entry(self):
        pass