from dataclasses import replace
from re import T
import pandas as pd
import numpy as np
import os

pd_list = []
for file in os.listdir('/Users/yan/Downloads/temp'):
    try:
        data = pd.read_csv('/Users/yan/Downloads/temp/'+file)
        data.sort_index(ascending=False,inplace=True)
        data = data[['代码','名称','上市日期','报告时间','净资产收益率']]
        data['净资产收益率'] = data['净资产收益率'].astype(np.float64)
        data['10年平均ROE'] = data['净资产收益率'].rolling(10).mean()
        data['10年最低ROE'] = data['净资产收益率'].rolling(10).min()
        data = data[(data['10年平均ROE'] >= 20) & (data['10年最低ROE'] >= 15)]
        data = data.dropna()
        pd_list.append(data)
    except Exception as e:
        print('/Users/yan/Downloads/temp/'+file, str(e))

all_data = pd.concat(pd_list)
all_data[all_data['报告时间'] == '2010-12-31'].sort_values(by='10年平均ROE',ascending=False).to_csv('2010-12-31.csv',index=False)
all_data[all_data['报告时间'] == '2011-12-31'].sort_values(by='10年平均ROE',ascending=False).to_csv('2011-12-31.csv',index=False)
all_data[all_data['报告时间'] == '2012-12-31'].sort_values(by='10年平均ROE',ascending=False).to_csv('2012-12-31.csv',index=False)
all_data[all_data['报告时间'] == '2013-12-31'].sort_values(by='10年平均ROE',ascending=False).to_csv('2013-12-31.csv',index=False)
all_data[all_data['报告时间'] == '2014-12-31'].sort_values(by='10年平均ROE',ascending=False).to_csv('2014-12-31.csv',index=False)
all_data[all_data['报告时间'] == '2015-12-31'].sort_values(by='10年平均ROE',ascending=False).to_csv('2015-12-31.csv',index=False)
all_data[all_data['报告时间'] == '2016-12-31'].sort_values(by='10年平均ROE',ascending=False).to_csv('2016-12-31.csv',index=False)
all_data[all_data['报告时间'] == '2017-12-31'].sort_values(by='10年平均ROE',ascending=False).to_csv('2017-12-31.csv',index=False)
all_data[all_data['报告时间'] == '2018-12-31'].sort_values(by='10年平均ROE',ascending=False).to_csv('2018-12-31.csv',index=False)
all_data[all_data['报告时间'] == '2019-12-31'].sort_values(by='10年平均ROE',ascending=False).to_csv('2019-12-31.csv',index=False)
all_data[all_data['报告时间'] == '2020-12-31'].sort_values(by='10年平均ROE',ascending=False).to_csv('2020-12-31.csv',index=False)
all_data[all_data['报告时间'] == '2021-12-31'].sort_values(by='10年平均ROE',ascending=False).to_csv('2021-12-31.csv',index=False)
