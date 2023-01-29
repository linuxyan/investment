# 导入tushare
import datetime
import time

import pandas as pd
import tushare as ts

# 初始化pro接口
pro = ts.pro_api('a44e2a405b4b8abc8373f202480c3bfffdcaa4e7b3b5a35613d851cd')

end_year = 2021  # 获取结束年报年份
end_date = str(end_year) + '1231'
start_date = str(end_year - 9) + '1231'  # 获取年报开始日期 (最近10年)
list_date = str(end_year - 6) + '1231'  # 获取上市日期(大于7年，年报可以采用3年上市前的数据)

print(start_date,end_date,list_date)

R15 = pd.read_csv('R15.csv')
R15_list = R15['证券代码'].values.tolist() # 长期跟踪R15

# 拉取数据
while True:
    all_stocks = pro.stock_basic(list_status="L", fields=["ts_code", "name", "industry", "list_date"])
    if not all_stocks.empty:
        break

all_stocks = all_stocks[all_stocks['list_date'] <= str(list_date)]
all_stocks.reset_index(drop=True, inplace=True)

R15_pd = []
for index, row in all_stocks.iterrows():
    # 拉取数据
    print(index, '/', all_stocks.shape[0], row['ts_code'], row['name'], len(R15_pd))
    while True:
        fina_data = pro.fina_indicator(
            **{
                "ts_code": row['ts_code'],
                "ann_date": "",
                "start_date": "",
                "end_date": "",
                "period": "",
                "update_flag": 1,
                "limit": "",
                "offset": "",
            },
            fields=["ts_code", "end_date", "roe", "debt_to_assets", "grossprofit_margin", "update_flag"],
        )
        if not fina_data.empty:
            break
    fina_data = fina_data[(fina_data['end_date'] >= str(start_date)) & (fina_data['end_date'] <= str(end_date))]
    fina_data["end_date"] = pd.to_datetime(fina_data["end_date"])
    fina_data = fina_data.resample(on="end_date", rule="Y").last()
    if (fina_data['roe'].min() >= 15 and fina_data['roe'].mean() >= 20) or (row['ts_code'] in R15_list):
        is_R15 = None   # 是否长期跟踪的R15
        if row['ts_code'] in R15_list:
            is_R15 = '长期'
        R15_pd.append(
            [
                row['ts_code'],
                row['name'],
                is_R15,
                round(fina_data['roe'].mean(), 2),
                round(fina_data['roe'].min(), 2),
                round(fina_data['grossprofit_margin'].max(), 2),
                round(fina_data['debt_to_assets'].min(), 2),
            ]
        )

    time.sleep(0.2)

R15_pd = pd.DataFrame(R15_pd, columns=['证券代码', '证券简称', '跟踪时间','平均ROE', '最小ROE', '最大负债率', '最小毛利率'])
R15_pd.to_csv('2022_R15.csv', index=False, encoding='utf_8_sig')
