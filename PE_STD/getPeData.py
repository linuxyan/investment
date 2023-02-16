import datetime
import tushare as ts
import pandas as pd
import time

# 初始化pro接口
pro = ts.pro_api('a44e2a405b4b8abc8373f202480c3bfffdcaa4e7b3b5a35613d851cd')

end_date = datetime.datetime.now()
start_date = end_date - datetime.timedelta(weeks=(10 * 52))
print('Get Data: ', int(start_date.strftime('%Y%m%d')), int(end_date.strftime('%Y%m%d')))

R15 = pd.read_csv('2022_R15.csv')
for _, row in R15.iterrows():
    print(row['证券代码'])
    while True:
        df = pro.daily_basic(
            **{
                "ts_code": row['证券代码'],
                "trade_date": "",
                "start_date": int(start_date.strftime('%Y%m%d')),
                "end_date": int(end_date.strftime('%Y%m%d')),
                "limit": "",
                "offset": "",
            },
            fields=[
                "ts_code",
                "trade_date",
                "close",
                "pe_ttm",
                "ps_ttm",
                "dv_ttm",
                "total_share",
                "total_mv",
            ],
        )
        if not df.empty:
            break

    df['证券简称'] = row['证券简称']
    df = df[
        [
            '证券简称',
            "ts_code",
            "trade_date",
            "close",
            "pe_ttm",
            "ps_ttm",
            "dv_ttm",
            "total_share",
            "total_mv",
        ]
    ]
    df.to_csv('data/%s_pe.csv' % row['证券代码'], index=False, encoding='utf_8_sig')
    time.sleep(0.5)
