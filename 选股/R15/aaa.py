# 导入tushare
import pandas as pd
import tushare as ts
import numpy as np
# 初始化pro接口
pro = ts.pro_api('a44e2a405b4b8abc8373f202480c3bfffdcaa4e7b3b5a35613d851cd')

# 获取分红数据
dividend_df = pro.dividend(ts_code="600519.SH", fields=[
                                            "ts_code",
                                            "end_date",
                                            "pay_date",
                                            "update_flag",
                                            "base_share",
                                            "cash_div"
                                        ])
dividend_df = dividend_df[dividend_df['cash_div'] > 0]
dividend_df.drop_duplicates(subset=['ts_code','end_date','pay_date','cash_div'],keep='first',inplace=True)
dividend_df['year'] = dividend_df.end_date.str[0:4]
dividend_df = dividend_df[['ts_code','year','base_share','cash_div']].groupby(['ts_code','year','base_share'], as_index=False).sum()

# print(dividend_df)


# 获取总收入和净利润
income_df = pro.income(**{
            "ts_code": "600519.SH",
            "end_type": 4,
        }, fields=[
            "ts_code",
            "ann_date",
            "report_type",
            "end_type",
            "total_revenue",
            "update_flag",
            "compr_inc_attr_p"
        ])
income_df.drop_duplicates(subset=['ts_code','ann_date','report_type','end_type'],keep='first',inplace=True)
income_df.dropna(inplace=True)
income_df['year'] = income_df.ann_date.str[0:4]
income_df = income_df[['ts_code','year','total_revenue','compr_inc_attr_p']]
print(income_df)

df = pd.merge(income_df,dividend_df)
df['分红金额(亿)'] = df['base_share'] * df['cash_div'] / 10000
df['分红率'] = np.round(df['base_share'] * df['cash_div'] * 10000 / df['compr_inc_attr_p'] * 100, 2)
df['净利润率'] = np.round(df['compr_inc_attr_p'] / df['total_revenue'] * 100,2)
df['total_revenue'] = df['total_revenue'] / 100000000
df['compr_inc_attr_p'] = df['compr_inc_attr_p'] / 100000000
print(df)