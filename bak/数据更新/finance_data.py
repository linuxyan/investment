import os
import time

import constant
import pandas as pd
import requests
import tushare as ts


class FinanceData:
    def __init__(
        self,
    ) -> None:
        self.tushare_token = 'a44e2a405b4b8abc8373f202480c3bfffdcaa4e7b3b5a35613d851cd'
        self.session = requests.Session()
        main_url = 'https://xueqiu.com/'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
        }
        self.session.get(url=main_url, headers=self.headers)

    def Codes(self):
        pro = ts.pro_api(self.tushare_token)
        data = pro.stock_basic(fields='ts_code,name,area,industry,list_date')
        data['list_date'] = data['list_date'].astype(int)
        print(data)
        return data

    def Getindex(self):
        code_list = self.Codes()['ts_code'].values.tolist()
        code_data = []
        for code in code_list:
            print(code, code_list.index(code))
            code = code.split('.')[1] + code.split('.')[0]

            if os.path.exists('temp/%s.csv' % code) or 'BJ' in code:
                continue

            info_url = 'https://stock.xueqiu.com/v5/stock/f10/cn/company.json?symbol=%s' % code
            info_response = self.session.get(url=info_url, headers=self.headers)
            info_data = info_response.json()
            listed_date = info_data['data']['company']['listed_date']
            if not listed_date:
                listed_date = time.time() * 1000
            time.sleep(2)

            url = (
                'https://stock.xueqiu.com/v5/stock/finance/cn/indicator.json?symbol=%s&type=Q4&is_detail=true&count=22&timestamp='
                % code
            )
            response = self.session.get(url=url, headers=self.headers)
            data = response.json()
            quote_name = data['data']['quote_name']
            data = data['data']['list']
            if not data:
                continue
            temp_data = []
            for data_item in data:
                # if data_item['report_date'] < listed_date:
                #     break  # 剔除上市之前的年报
                temp_dict = {
                    '代码': code,
                    '名称': quote_name,
                    '行业': info_data['data']['company']['affiliate_industry']['ind_name'],
                    '上市日期': time.strftime("%Y-%m-%d", time.localtime(listed_date / 1000)),
                }
                for key in constant.column_name.keys():
                    value = data_item[key]
                    if isinstance(value, list):
                        value = data_item[key][0]
                    if key == 'report_date':
                        value = time.strftime("%Y-%m-%d", time.localtime(data_item[key] / 1000))
                    temp_dict[constant.column_name[key]] = value
                temp_data.append(temp_dict)
            code_data += temp_data
            if temp_data:
                pd.DataFrame(temp_data).to_csv('temp/%s.csv' % code, index=False)
            time.sleep(3)


data = FinanceData()
data.Getindex()
