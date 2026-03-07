from typing import Annotated
import akshare as ak
from datetime import datetime, timedelta

import pandas as pd


def get_stock_news(
        ticker: Annotated[str, "eg: sh.600004"],
        curr_date: Annotated[str, "当前日期，格式：YYYY-MM-DD"],
        look_back_days: int = 7
) -> str:
    """
    Args:
        ticker: 股票代码（如：000001、0700.HK、AAPL）
        curr_date: 当前日期（格式：YYYY-MM-DD）
        look_back_days: 往前回顾的天数 (default 7)

    Returns:
        str: 新闻分析报告
    """
    # 计算新闻查询的日期范围
    end_date = datetime.strptime(curr_date, '%Y-%m-%d')
    start_date = end_date - timedelta(days=look_back_days)
    start_date_str = start_date.strftime('%Y-%m-%d')

    result_data = []
    clean_ticker = ticker.replace('sh.', '').replace('sz.', '')
    try:
        # 获取东方财富新闻
        em_news_df = ak.stock_news_em(symbol=clean_ticker)

        if em_news_df is not None and not em_news_df.empty:
            # 格式化东方财富新闻
            em_news_items = []
            for _, row in em_news_df.iterrows():
                # AKShare 返回的字段名
                news_title = row.get('新闻标题', '') or row.get('标题', '')
                news_time = row.get('发布时间', '') or row.get('时间', '')
                news_url = row.get('新闻链接', '') or row.get('链接', '')

                news_item = f"- **{news_title}** [{news_time}]({news_url})"
                em_news_items.append(news_item)

            # 添加到结果中
            if em_news_items:
                em_news_text = "\n".join(em_news_items)
                result_data.append(f"## 东方财富新闻\n{em_news_text}")
    except Exception as e:
        result_data.append(f"## 东方财富新闻\n获取失败: {e}")

    try:
        lookback_days = 7
        report_news_df = pd.DataFrame()
        for i in range(lookback_days, -1, -1):
            date_str = str(end_date - timedelta(days=i))[:10]
            date_str = date_str.replace('-', '')
            tmp_df = ak.stock_notice_report(symbol="全部", date=date_str)

            report_news_df = pd.concat([report_news_df, tmp_df])

        symbol_report_df = report_news_df[report_news_df["代码"]==clean_ticker]
        if symbol_report_df is not None and not symbol_report_df.empty:
            report_news_items = []
            for _, row in symbol_report_df.iterrows():
                report_title = row.get("公告标题", "") or row.get('标题', '')
                report_time = row.get("公告日期", "")  or row.get('日期', '')
                report_url = row.get("网址", "") or row.get("链接", "")

                report_item = f"- **{report_title}** [{report_time}]({report_url})"
                report_news_items.append(report_item)

            if report_news_items:
                report_news_text = "\n".join(report_news_items)
                result_data.append(f"## 公司公告\n{report_news_text}")
    except Exception as e:
        result_data.append(f"## 公司公告信息获取失败: {e}")

    # 组合所有数据
    combined_result = f"""# {ticker} 新闻与公告分析
**新闻时间范围**: {start_date_str} 至 {curr_date}

{chr(10).join(result_data)}
        """
    return combined_result
