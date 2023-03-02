# 导入tushare
import datetime
import time

import numpy as np
import pandas as pd
import tushare as ts

# 初始化pro接口
pro = ts.pro_api('a44e2a405b4b8abc8373f202480c3bfffdcaa4e7b3b5a35613d851cd')

end_date = datetime.datetime.now()
end_year = int(end_date.strftime('%Y'))
if int(end_date.strftime('%m%d')) >= 501:
    R15FileName = end_year
else:
    R15FileName = end_year - 1

R15File = '%s_R15.csv' % str(R15FileName)

print('Get Finance Data: ', R15File)

R15 = pd.read_csv(R15File)
for _, row in R15.iterrows():
    print(row['证券代码'])

    while True:
        # 基础数据
        base_df = pro.stock_basic(ts_code=row['证券代码'], fields=["ts_code", "industry", "list_date"])
        if not base_df.empty:
            break
    base_df['list_date'] = np.int32(base_df.list_date.str[0:4])

    while True:
        # 获取分红数据
        dividend_df = pro.dividend(
            ts_code=row['证券代码'], fields=["ts_code", "end_date", "pay_date", "update_flag", "base_share", "cash_div"]
        )
        if not dividend_df.empty:
            break
    dividend_df = dividend_df[dividend_df['cash_div'] > 0]
    dividend_df.drop_duplicates(subset=['ts_code', 'end_date', 'pay_date', 'cash_div'], keep='first', inplace=True)
    dividend_df['year'] = dividend_df.end_date.str[0:4]
    dividend_df = (
        dividend_df[['ts_code', 'year', 'base_share', 'cash_div']]
        .groupby(['ts_code', 'year', 'base_share'], as_index=False)
        .sum()
    )
    # print(dividend_df)

    while True:
        # 获取总收入和净利润
        income_df = pro.income(
            **{
                "ts_code": row['证券代码'],
                "end_type": 4,
            },
            fields=[
                "ts_code",
                "end_date",
                "report_type",
                "end_type",
                "total_revenue",
                "update_flag",
                "compr_inc_attr_p",
            ],
        )
        if not income_df.empty:
            break
    income_df.drop_duplicates(subset=['ts_code', 'end_date', 'report_type', 'end_type'], keep='first', inplace=True)
    income_df.dropna(inplace=True)
    income_df['year'] = income_df.end_date.str[0:4]
    income_df = income_df[['ts_code', 'year', 'total_revenue', 'compr_inc_attr_p']]
    # print(income_df)

    # 资产负债率 = total_liab / total_assets
    while True:
        balance_df = pro.balancesheet(
            **{
                "ts_code": row['证券代码'],
                "end_type": 4,
            },
            fields=[
                "ts_code",
                "end_date",
                "total_assets",
                "total_liab",
            ],
        )
        if not balance_df.empty:
            break
    balance_df.drop_duplicates(subset=['ts_code', 'end_date'], keep='first', inplace=True)
    balance_df.dropna(inplace=True)
    balance_df['year'] = balance_df.end_date.str[0:4]
    balance_df['liab_ratio'] = np.round(balance_df['total_liab'] / balance_df['total_assets'] * 100, 2)
    balance_df = balance_df[['ts_code', 'year', 'liab_ratio']]

    # ROE
    while True:
        roe_data = pro.fina_indicator(
            **{
                "ts_code": row['证券代码'],
            },
            fields=["ts_code", "end_date", "roe"],
        )
        if not roe_data.empty:
            break
    roe_data['end_date_str'] = roe_data.end_date.str[-4:]
    roe_data['year'] = roe_data.end_date.str[0:4]
    roe_data = roe_data[roe_data['end_date_str'] == '1231']
    roe_data.drop_duplicates(subset=['ts_code', 'end_date', 'roe'], keep='first', inplace=True)
    roe_data = roe_data[['ts_code', 'year', 'roe']]

    df = pd.merge(base_df, roe_data)
    df = pd.merge(df, income_df)
    df = pd.merge(df, dividend_df)
    df = pd.merge(df, balance_df)
    df['分红金额(亿)'] = np.round(df['base_share'] * df['cash_div'] / 10000, 4)
    df['分红率'] = np.round(df['base_share'] * df['cash_div'] * 10000 / df['compr_inc_attr_p'] * 100, 2)
    df['净利润率'] = np.round(df['compr_inc_attr_p'] / df['total_revenue'] * 100, 2)
    df['total_revenue'] = np.round(df['total_revenue'] / 100000000, 4)
    df['compr_inc_attr_p'] = np.round(df['compr_inc_attr_p'] / 100000000, 4)
    df.rename(
        columns={
            'list_date': '上市年份',
            'industry': '行业',
            'total_revenue': '营业总收入(亿)',
            'compr_inc_attr_p': '净利润(亿)',
            'base_share': '股本(万)',
            'cash_div': '每股分红',
            'liab_ratio': '负债率',
        },
        inplace=True,
    )

    # print(df)
    df.to_csv('data/%s_finance.csv' % row['证券代码'], index=False, encoding='utf_8_sig')
    time.sleep(0.5)
