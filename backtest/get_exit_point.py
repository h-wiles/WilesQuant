import pandas as pd

class ExitPoint:
    def __init__(self, code, signal_col="signal", price_col='close'):
        self.df = pd.read_csv(f"./data/price_data/{code}.csv")
        self.signal_col = signal_col
        self.price_col = price_col

    def fixed_tp_sl(self, entry_df, tp=0.02, sl=0.01):
        """固定比例止盈止损策略：2%止盈，1%止损，达到比例就出场，非收盘价出场"""
        df = entry_df.copy()
        if "signal" not in df.columns:
            raise ValueError("the input df must have 'signal' column")
        entry_price = 0  # 买入价
        position = 0
        n = len(df)

        for i in range(n):
            price = df.loc[i, self.price_col]
            signal = df.loc[i, self.signal_col]

            # ===== 无持仓 → 看是否买入 =====
            if position == 0 and signal == 1:
                entry_price = price
                position = 1

            if position > 0:
                pnl = (price - entry_price) / entry_price

                if pnl >= tp or pnl <= -sl:
                    entry_price = 0
                    position = 0

                    if df.loc[i, self.signal_col] == 0:     # 入场出场点冲突时保留入场点
                        df.loc[i, self.signal_col] = -1
        return df

    def fix_hold_days(self, entry_df, hold_days):
        df = entry_df.copy()
        if "signal" not in df.columns:
            raise ValueError("the input df must have 'signal' column")
        entry_index = None
        position = 0

        for i in range(len(df)):
            signal = df.loc[i, self.signal_col]

            if position == 0 and signal == 1:
                position = 1
                entry_index = i

            if position == 1:
                if i - entry_index >= hold_days:
                    df.loc[i, self.signal_col] = -1
                    position = 0
                    entry_index = None
        return df

