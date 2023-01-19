import requests
import pandas as pd
import time

# market_url pea_url
urls = ['https://eniu.com/chart/marketvaluea/code', 'https://eniu.com/chart/pea/code/t/all']
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Safari/605.1.15'
}


R15 = pd.read_csv('2022_R15.csv')
for _, row in R15.iterrows():
    time.sleep(2)
    code_data = pd.DataFrame()
    code = str(row['证券代码']).split('.')[1].lower() + str(row['证券代码']).split('.')[0]
    for url in urls:
        response = requests.get(url.replace('code', code), headers=headers)
        pd_data = pd.DataFrame(response.json())
        pd_data.set_index('date')
        if code_data.empty:
            code_data = pd_data
        else:
            code_data = pd.merge(code_data, pd_data, on=['date'], how='left')
    code_data['code'] = code
    code_data['name'] = row['证券简称']
    code_data = code_data[['code', 'name', 'date', 'market_value', 'pe_ttm', 'price']]
    code_data.to_csv('data/%s.csv' % code)


# (市值 / 市盈率 )    # 净利润
# 净利润 * 目标市盈率  # 目标市值
# (市值 / 股价 )      # 总股本
# 目标市值 / 总股本 =  # 目标股价

# (23176.22 / 41.57)  * 38.91 / (23176.22 / 1844.95)
