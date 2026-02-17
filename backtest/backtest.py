import matplotlib.pyplot as plt
from get_entry_point import EntryPoint
import pandas as pd
import warnings
warnings.filterwarnings("ignore")


def backtest_tp_sl(df, price_col='close', signal_col='signal',
                   initial_cash=10000, tp=0.02, sl=0.01,
                   plot_equity_curve=True):
    """
    带止盈止损的回测, 无手续费

    signal: 1=买入信号
    tp: 止盈比例 (0.02 = 2%)
    sl: 止损比例 (0.01 = 1%)
    """

    df = df.copy()
    n = len(df)

    cash = initial_cash
    position = 0  # 持仓股数
    entry_price = 0  # 买入价
    equity_curve = []

    for i in range(n):
        price = df.loc[i, price_col]
        signal = df.loc[i, signal_col]

        # ===== 无持仓 → 看是否买入 =====
        if position == 0 and signal == 1:
            position = cash // price        # 购买股数
            entry_price = price
            cash = cash - position * price      # 剩余资金

        # ===== 已持仓 → 检查止盈止损 =====
        if position > 0:
            pnl = (price - entry_price) / entry_price

            if pnl >= tp or pnl <= -sl:
                if pnl > 0:
                    cash += position * entry_price * (1 + tp)
                else:
                    cash += position * entry_price * (1 - sl)
                position = 0
                entry_price = 0

        # ===== 计算每日资产 =====
        equity = cash + position * price
        equity_curve.append(equity)

    df['equity'] = equity_curve
    df['cum_return'] = df['equity'] / initial_cash - 1

    if plot_equity_curve:
        plt.figure(figsize=(10, 5))
        plt.plot(pd.to_datetime(df["date"]), df['cum_return'])
        plt.title("Equity Curve (TP 2% / SL 1%)")
        plt.ylabel("Return")
        plt.show()

    return df


def main_backtest(code, strategy):
    ep = EntryPoint(code)
    if strategy == "ma5 diverge":
        entry_df = ep.ma5_diverge_entry()
    elif strategy == "kdj oversold":
        entry_df = ep.kdj_oversold_entry()
    elif strategy == "macd golden cross":
        entry_df = ep.macd_golden_cross_entry()
    elif strategy == "macd bullish divergence":
        entry_df = ep.macd_bullish_divergence_entry()
    elif strategy == "volume breakout":
        entry_df = ep.volume_breakout_entry()
    else:
        raise ValueError("strategy not supported")

    res = backtest_tp_sl(entry_df, price_col="close", signal_col="signal")
    return res


if __name__ == '__main__':
    response = main_backtest("sh.600004", strategy="ma5 diverge")
    print(response)