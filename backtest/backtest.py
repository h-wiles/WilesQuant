import pandas as pd
from MyUtils import get_ma_data
import numpy as np
from collections import defaultdict
import json
import warnings
warnings.filterwarnings("ignore")


def backtest_tp_sl(df, price_col='close', signal_col='signal',
                   initial_cash=10001, tp=0.02, sl=0.01):
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

    return df




