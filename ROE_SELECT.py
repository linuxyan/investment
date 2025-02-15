import datetime
import time
import akshare as ak
import pandas as pd

# 获取所有股票的列表
# stock_sh_list = ak.stock_info_sh_name_code(symbol="主板A股")
# stock_sz_list = ak.stock_info_sz_name_code(symbol="A股列表")

# stock_sh_list = stock_sh_list[["证券代码", "证券简称"]]
# stock_sz_list = stock_sz_list[["A股代码", "A股简称"]]
# stock_sz_list = stock_sz_list.rename(
#     columns={"A股代码": "证券代码", "A股简称": "证券简称"}
# )

# stock_list = pd.concat([stock_sh_list, stock_sz_list], ignore_index=True)


stock_list = pd.read_pickle("selected_stocks.pkl")
print(stock_list)
# 筛选符合条件的股票
selected_stocks = []


# 获取经营现金流净额(是否赚到了真钱)
def calculate_operating_cash_flow():
    cash_flow_dfs = []
    current_year = datetime.datetime.now().year - 1
    recent_8_years = [current_year - i for i in range(8)]  # 获取最近8年的年份
    for year in recent_8_years:
        print(year)
        cash_flow_df = ak.stock_xjll_em(date=f"{year}1231")
        cash_flow_df = cash_flow_df[['股票代码', '股票简称', '经营性现金流-现金流量净额']]
        cash_flow_df = cash_flow_df.rename(columns={"股票代码": "股票代码", "股票简称": "证券简称","经营性现金流-现金流量净额":"经营性现金流-现金流量净额"})
        cash_flow_df['报告期'] = year
        cash_flow_dfs.append(cash_flow_df)
        time.sleep(1)
    cash_flow_dfs = pd.concat(cash_flow_dfs, ignore_index=True)
    return cash_flow_dfs


cash_flow_dfs = calculate_operating_cash_flow()

# 遍历每个股票
for index, stock in enumerate(stock_list["证券代码"]):
        print(index, len(stock_list["证券代码"]))
        stock_name = stock_list[stock_list["证券代码"] == stock]["证券简称"].values[0]

        # 获取上市日期
        stock_info = ak.stock_individual_info_em(symbol=stock)
        listing_date = stock_info[stock_info["item"] == "上市时间"]["value"].values[0]
        industry = stock_info[stock_info["item"] == "行业"]["value"].values[0]
        listing_year = int(str(listing_date)[:4])  # 上市年份

        # 获取该股票的财务数据（假设这里返回的是按年分的ROE数据）
        financial_data = ak.stock_financial_abstract_ths(
            symbol=stock, indicator="按年度"
        )

        # 筛选近7年的ROE数据
        last_7_years_roe = financial_data.head(7)[
            [
                "报告期",
                "扣非净利润",
                "扣非净利润同比增长率",
                "净资产收益率",
                "净资产收益率-摊薄",
            ]
        ]

        last_7_years_roe["扣非净利润"] = (
            last_7_years_roe["扣非净利润"]
            .replace({"亿": "*1e8", "万": "*1e4"}, regex=True)
            .map(pd.eval)
            .astype(float)
        )
        last_7_years_roe["扣非净利润"] = last_7_years_roe["扣非净利润"].round(2)
        last_7_years_roe["扣非净利润同比增长率"] = (
            last_7_years_roe["扣非净利润同比增长率"]
            .replace("%", "", regex=True)
            .astype(float)
        )
        last_7_years_roe["净资产收益率"] = (
            last_7_years_roe["净资产收益率"].replace("%", "", regex=True).astype(float)
        )
        last_7_years_roe["净资产收益率-摊薄"] = (
            last_7_years_roe["净资产收益率-摊薄"]
            .replace("%", "", regex=True)
            .astype(float)
        )

        min_year = int(last_7_years_roe['报告期'].min())

        # print(last_7_years_roe)
        last_7_years_roe["股票代码"] = stock
        last_7_years_roe["证券简称"] = stock_name

        last_7_years = pd.merge(last_7_years_roe, cash_flow_dfs, on=['股票代码', '证券简称', '报告期'])

        last_7_years['经盈现金_净利润'] = last_7_years['经营性现金流-现金流量净额'] / last_7_years['扣非净利润']
        condition = last_7_years[last_7_years['经盈现金_净利润'] > 0.8].shape[0]

        # 检查是否有7年的数据且每年ROE都大于15%
        if (
            len(last_7_years) == 7
            and min_year >= listing_year    # 年报数据的最小年份，要大于等于上市年份。
            and all(last_7_years["净资产收益率-摊薄"] >= 15)
            and all(last_7_years["扣非净利润"] > 0)
            and condition >= 5        # 7年有5年经营现金流金额大于净利润0.8倍
        ):
            selected_stocks.append([stock, stock_name, industry])
            print(last_7_years)
        time.sleep(0.5)

# 输出符合条件的股票列表
df_selected_stocks = pd.DataFrame(selected_stocks, columns=["证券代码", "证券简称", "行业"])
df_selected_stocks.to_pickle("selected_stocks.pkl")
# print(f"符合条件的股票: {selected_stocks}")
