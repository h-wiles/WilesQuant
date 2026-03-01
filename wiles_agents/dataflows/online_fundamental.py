import baostock as bs
import pandas as pd
from collections import defaultdict

def get_industry_info(code):
    df = pd.read_csv("./data/stock_industry.csv")
    industry = df[df["code"]==code]["industry"].iloc[0]
    code_name = df[df["code"]==code]["code_name"].iloc[0]
    result = defaultdict(str)
    result["industry"] = industry
    if "银行" in code_name:      # 银行板块股票
        industry_analysis = "银行业整体增长稳定，受益于经济发展和金融深化。数字化转型和财富管理业务是主要增长点。"
    elif code.split(".")[-1].startswith("300"):     # 科创板股票
        industry_analysis = "创业板公司通常具有较高的成长潜力，但也伴随着较高的风险。需要关注技术创新和市场拓展能力。"
    else:
        industry_analysis = "成长潜力需要结合具体行业和公司基本面分析。建议关注行业发展趋势和公司竞争优势。"

    result["industry_analysis"] = industry_analysis
    result["code_name"] = code_name
    return industry


def get_valuation_data(code, curr_date):
    rs = bs.query_history_k_data_plus(code,
                                      "date,code,close,peTTM,pbMRQ,psTTM,pcfNcfTTM",
                                      start_date=curr_date, end_date=curr_date,
                                      frequency="d", adjustflag="2")
    result_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        result_list.append(rs.get_row_data())
    df = pd.DataFrame(result_list, columns=rs.fields)

    result = defaultdict(str)
    result["peTTM"] = df["peTTM"].iloc[0]
    result["pbMRQ"] = df["pbMRQ"].iloc[0]
    result["psTTM"] = df["psTTM"].iloc[0]
    result["pcfNcfTTM"] = df["pcfNcfTTM"].iloc[0]

    return result

def get_profit_data(code, curr_date):
    # 查询季频估值指标盈利能力
    profit_list = []
    year, quarter = curr_date.split("-")[0], 1+int(curr_date.split("-")[1]) // 3
    rs_profit = bs.query_profit_data(code=code, year=year, quarter=quarter)
    while (rs_profit.error_code == '0') & rs_profit.next():
        profit_list.append(rs_profit.get_row_data())
    result_profit = pd.DataFrame(profit_list, columns=rs_profit.fields)

    result = defaultdict(str)
    result["roeAvg"] = result_profit["roeAvg"].iloc[0]     # 净资产收益率(平均)(%)
    result["npMargin"] = result_profit["npMargin"].iloc[0]    # 销售净利率(%)
    result["gpMargin"] = result_profit["gpMargin"].iloc[0]     # 销售毛利率(%)
    result["netProfit"] = result_profit["netProfit"].iloc[0]     # 净利润(元)
    result["epsTTM"] = result_profit["epsTTM"].iloc[0]         # 每股收益
    result["MBRevenue"] = result_profit["MBRevenue"].iloc[0]        # 主营营业收入(元)
    result["totalShare"] = result_profit["totalShare"].iloc[0]        # 总股本 
    result["liqaShare"] = result_profit["liqaShare"].iloc[0]         # 流通股本

    return result

def get_growth_data(code, curr_date):
    growth_list = []
    year, quarter = curr_date.split("-")[0], 1+int(curr_date.split("-")[1]) // 3
    rs_growth = bs.query_growth_data(code=code, year=year, quarter=quarter)
    while (rs_growth.error_code == '0') & rs_growth.next():
        growth_list.append(rs_growth.get_row_data())
    result_growth = pd.DataFrame(growth_list, columns=rs_growth.fields)

    result = defaultdict(str)
    result["YOYEquity"] = result_growth["YOYEquity"].iloc[0]        # 净资产同比增长率
    result["YOYAsset"] = result_growth["YOYAsset"].iloc[0]         # 总资产同比增长率
    result["YOYNI"] = result_growth["YOYNI"].iloc[0]            # 净利润同比增长率
    result["YOYEPSBasic"] = result_growth["YOYEPSBasic"].iloc[0]            # 基本每股收益同比增长率
    result["YOYPNI"] = result_growth["YOYPNI"].iloc[0]         # 归属母公司股东净利润同比增长率

    return result


def get_balance_data(code, curr_date):
    # 偿债能力
    balance_list = []
    year, quarter = curr_date.split("-")[0], 1+int(curr_date.split("-")[1]) // 3
    rs_balance = bs.query_balance_data(code=code, year=year, quarter=quarter)
    while (rs_balance.error_code == '0') & rs_balance.next():
        balance_list.append(rs_balance.get_row_data())
    result_balance = pd.DataFrame(balance_list, columns=rs_balance.fields)

    result = defaultdict(str)
    result["currentRatio"] = result_balance["currentRatio"].iloc[0]      # 流动比率
    result["quickRatio"] = result_balance["quickRatio"].iloc[0]        # 速动比率
    result["cashRatio"] = result_balance["cashRatio"].iloc[0]         # 现金比率
    result["YOYLiability"] = result_balance["YOYLiability"].iloc[0]      # 总负债同比增长率
    result["liabilityToAsset"] = result_balance["liabilityToAsset"].iloc[0]           # 资产负债率
    return result


def get_stock_fundamental(code: str, curr_date) -> str:
    """
    基于股票数据生成真实的基本面分析报告
    """

    bs.login()
    industry_info = get_industry_info(code)
    valuation_data = get_valuation_data(code, curr_date)
    profit_data = get_profit_data(code, curr_date)
    growth_data = get_growth_data(code, curr_date)
    balance_data = get_balance_data(code, curr_date)
    price_data = pd.read_csv(f"../../data/price_data/{code}.csv")

    company_name = industry_info.get("code_name", "N/A")
    current_price = price_data["close"].iloc[-1]
    volume = price_data["volume"].iloc[-1]
    change_pct = (current_price-price_data["close"].iloc[-2]) / price_data["close"].iloc[-2]

    report = f"""# 中国A股基本面分析报告 - {company_name}

    ## 📊 股票基本信息
    - **股票代码**: {code}
    - **股票名称**: {company_name}
    - **所属行业**: {industry_info.get('industry', "未知")}
    - **当前股价**: {current_price}
    - **涨跌幅**: {change_pct}
    - **成交量**: {volume}
    - **分析日期**: {curr_date}
    
    ## 💰 财务数据分析
    
    ### 估值指标
    - **总市值**: {current_price * profit_data.get("totalShare")}
    - **滚动市盈率(PE_TTM)**: {valuation_data.get('peTTM', 'N/A')}
    - **市净率(PB)**: {valuation_data.get('pbMRQ', 'N/A')}
    - **滚动市销率(PS_TTM)**: {valuation_data.get('psTTM', 'N/A')}
    - **滚动市现率(pcfNcf_TTM)**: {valuation_data.get('pcfNcfTTM', 'N/A')}
    
    ### 盈利能力指标
    - **净资产收益率(平均)(%)**: {profit_data.get('roeAvg', 'N/A')}
    - **销售净利率(%)**: {profit_data.get('npMargin', 'N/A')}
    - **销售毛利率(%)**: {profit_data.get('gpMargin', 'N/A')}
    - **净利润(元)**: {profit_data.get('netProfit', 'N/A')}
    - **每股收益**: {profit_data.get('epsTTM', 'N/A')}
    - **主营营业收入(元)**: {profit_data.get('MBRevenue', 'N/A')}
    
    ### 成长能力指标
    - **净资产同比增长率**: {growth_data.get("YOYEquity", "N/A")}
    - **总资产同比增长率**: {growth_data.get("YOYAsset", "N/A")}
    - **净利润同比增长率**: {growth_data.get("YOYNI", "N/A")}
    - **基本每股收益同比增长率**: {growth_data.get("YOYEPSBasic", "N/A")}
    - **归属母公司股东净利润同比增长率**: {growth_data.get("YOYPNI", "N/A")}
    
    ### 偿债能力指标
    - **流动比率**: {balance_data.get("currentRatio", "N/A")}
    - **速动比率**: {balance_data.get("quickRatio", "N/A")}
    - **现金比率**: {balance_data.get("cashRatio", "N/A")}
    - **总负债同比增长率**: {balance_data.get("YOYLiability", "N/A")}
    - **资产负债率**: {balance_data.get("liabilityToAsset", "N/A")}
    
    ## 📈 行业分析
    
    ### 行业地位
    {industry_info['analysis']}
    
    """
    bs.logout()

    return report