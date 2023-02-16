# 导入tushare
import time
import pandas as pd
import tushare as ts
import numpy as np
# 初始化pro接口
pro = ts.pro_api('a44e2a405b4b8abc8373f202480c3bfffdcaa4e7b3b5a35613d851cd')

R15 = pd.read_csv('2022_R15.csv')
for _, row in R15.iterrows():
    print(row['证券代码'])
    while True:
        # 获取分红数据
        dividend_df = pro.dividend(ts_code=row['证券代码'], fields=[
                                                    "ts_code",
                                                    "end_date",
                                                    "pay_date",
                                                    "update_flag",
                                                    "base_share",
                                                    "cash_div"
                                                ])
        if not dividend_df.empty:
            break
    dividend_df = dividend_df[dividend_df['cash_div'] > 0]
    dividend_df.drop_duplicates(subset=['ts_code','end_date','pay_date','cash_div'],keep='first',inplace=True)
    dividend_df['year'] = dividend_df.end_date.str[0:4]
    dividend_df = dividend_df[['ts_code','year','base_share','cash_div']].groupby(['ts_code','year','base_share'], as_index=False).sum()
    # print(dividend_df)

    while True:
        # 获取总收入和净利润
        income_df = pro.income(**{
                    "ts_code": row['证券代码'],
                    "end_type": 4,
                }, fields=[
                    "ts_code",
                    "end_date",
                    "report_type",
                    "end_type",
                    "total_revenue",
                    "update_flag",
                    "compr_inc_attr_p"
                ])
        if not income_df.empty:
            break
    income_df.drop_duplicates(subset=['ts_code','end_date','report_type','end_type'],keep='first',inplace=True)
    income_df.dropna(inplace=True)
    income_df['year'] = income_df.end_date.str[0:4]
    income_df = income_df[['ts_code','year','total_revenue','compr_inc_attr_p']]
    # print(income_df)

    # 资产负债率 = total_liab / total_assets
    # df = pro.balancesheet(**{
    #     "ts_code": "600519.SH",
    #     "end_type": "4",
    # }, fields=[
    #     "ts_code",
    #     "end_date",
    #     "total_assets",
    #     "total_liab",
    #     "end_type"
    # ])
    # 毛利润率

    df = pd.merge(income_df,dividend_df)
    df['分红金额(亿)'] = np.round(df['base_share'] * df['cash_div'] / 10000,4)
    df['分红率'] = np.round(df['base_share'] * df['cash_div'] * 10000 / df['compr_inc_attr_p'] * 100, 2)
    df['净利润率'] = np.round(df['compr_inc_attr_p'] / df['total_revenue'] * 100,2)
    df['total_revenue'] = np.round(df['total_revenue'] / 100000000,4)
    df['compr_inc_attr_p'] = np.round(df['compr_inc_attr_p'] / 100000000,4)
    df.rename(columns={'total_revenue':'营业总收入(亿)','compr_inc_attr_p':'净利润(亿)','base_share':'股本(万)','cash_div':'每股分红'},inplace=True)

    # print(df)
    df.to_csv('data/%s_finance.csv' % row['证券代码'], index=False, encoding='utf_8_sig')
    time.sleep(0.5)