import matplotlib.pyplot as plt
from .get_entry_point import EntryPoint
from .get_exit_point import ExitPoint
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

def signal_clean(signal):
    """对入场出场信号进行处理，防止出现重复买入和重复卖出的情况"""
    result = []
    first_nonzero_seen = False
    last_nonzero = 0
    for s in signal:
        if s == 0:
            result.append(0)
            continue
        if not first_nonzero_seen:
            if s == 1:
                first_nonzero_seen = True
                result.append(1)
                last_nonzero = 1
            else:
                result.append(0)
            continue

        if s == last_nonzero:
            result.append(0)
        else:
            result.append(s)
            last_nonzero = s

    return result


def get_trade_performance(df, price_col='close', signal_col='signal',
                          initial_cash=10000):
    """
    获取入场出场策略等收益率等
    """

    df = df.copy()
    n = len(df)

    cash = initial_cash
    position = 0  # 持仓股数
    equity_curve = []

    signal = df[signal_col].tolist()
    df[signal_col] = signal_clean(signal)

    for i in range(n):
        price = df.loc[i, price_col]
        signal = df.loc[i, signal_col]

        # ===== 无持仓 → 看是否买入 =====
        if position == 0 and signal == 1:
            entry_price = price
            position = cash // entry_price        # 购买股数
            cash = cash - position * entry_price      # 剩余资金

        # ===== 已持仓 → 检查止盈止损 =====
        if position > 0 and signal == -1:
            exit_price = price
            cash += position * exit_price
            position = 0

        # ===== 计算每日资产 =====
        equity = cash + position * price
        equity_curve.append(equity)

    df['equity'] = equity_curve
    df['cum_return'] = df['equity'] / initial_cash - 1

    return df


def main_backtest(code, entry_strategy, exit_strategy, plot_equity_curve=True):
    enp = EntryPoint(code)
    exp = ExitPoint(code)
    if entry_strategy == "ma5_diverge":
        entry_df = enp.ma5_diverge_entry()
    elif entry_strategy == "kdj_oversold":
        entry_df = enp.kdj_oversold_entry()
    elif entry_strategy == "macd_golden_cross":
        entry_df = enp.macd_golden_cross_entry()
    elif entry_strategy == "macd_bullish_divergence":
        entry_df = enp.macd_bullish_divergence_entry()
    elif entry_strategy == "volume_breakout":
        entry_df = enp.volume_breakout_entry()
    else:
        raise ValueError("entry_strategy not supported")

    if exit_strategy == "fix_tp_sl":
        exit_df = exp.fixed_tp_sl(entry_df)
    elif exit_strategy == "fix_hold_days":
        exit_df = exp.fix_hold_days(entry_df, hold_days=3)
    elif exit_strategy == "kdj_overbuy":
        exit_df = exp.kdj_oversold_buy(entry_df)
    else:
        raise ValueError("exit_strategy not supported")

    res = get_trade_performance(exit_df, price_col="close", signal_col="signal")
    res = res.fillna(0)

    if plot_equity_curve:
        plt.figure(figsize=(10, 5))
        plt.plot(pd.to_datetime(res["date"]), res['cum_return'])
        plt.title("Total Return Curve")
        plt.ylabel("Return")
        plt.show()

    return res


if __name__ == '__main__':
    response = main_backtest("sh.600004", entry_strategy="ma5_diverge",
                             exit_strategy="fix_tp_sl")
    print(response)