from dataclasses import replace
from re import T
import pandas as pd
import numpy as np
import os

pd_list = []
for file in os.listdir('temp'):
    try:
        data = pd.read_csv('temp/'+file)
        data.sort_index(ascending=False,inplace=True)
        data = data[['代码','名称','上市日期','报告时间','净资产收益率']]
        data['净资产收益率'] = data['净资产收益率'].astype(np.float64)
        data['10年平均ROE'] = data['净资产收益率'].rolling(10).mean()
        data['10年最低ROE'] = data['净资产收益率'].rolling(10).min()
        data = data[(data['10年平均ROE'] >= 20) & (data['10年最低ROE'] >= 15)]
        data = data.dropna()
        pd_list.append(data)
    except Exception as e:
        print('temp/'+file, str(e))

all_data = pd.concat(pd_list)
all_data[all_data['报告时间'] == '2010-12-31'].sort_values(by='10年平均ROE',ascending=False).to_csv('select/2010-12-31_10.csv',index=False)
all_data[all_data['报告时间'] == '2011-12-31'].sort_values(by='10年平均ROE',ascending=False).to_csv('select/2011-12-31_10.csv',index=False)
all_data[all_data['报告时间'] == '2012-12-31'].sort_values(by='10年平均ROE',ascending=False).to_csv('select/2012-12-31_10.csv',index=False)
all_data[all_data['报告时间'] == '2013-12-31'].sort_values(by='10年平均ROE',ascending=False).to_csv('select/2013-12-31_10.csv',index=False)
all_data[all_data['报告时间'] == '2014-12-31'].sort_values(by='10年平均ROE',ascending=False).to_csv('select/2014-12-31_10.csv',index=False)
all_data[all_data['报告时间'] == '2015-12-31'].sort_values(by='10年平均ROE',ascending=False).to_csv('select/2015-12-31_10.csv',index=False)
all_data[all_data['报告时间'] == '2016-12-31'].sort_values(by='10年平均ROE',ascending=False).to_csv('select/2016-12-31_10.csv',index=False)
all_data[all_data['报告时间'] == '2017-12-31'].sort_values(by='10年平均ROE',ascending=False).to_csv('select/2017-12-31_10.csv',index=False)
all_data[all_data['报告时间'] == '2018-12-31'].sort_values(by='10年平均ROE',ascending=False).to_csv('select/2018-12-31_10.csv',index=False)
all_data[all_data['报告时间'] == '2019-12-31'].sort_values(by='10年平均ROE',ascending=False).to_csv('select/2019-12-31_10.csv',index=False)
all_data[all_data['报告时间'] == '2020-12-31'].sort_values(by='10年平均ROE',ascending=False).to_csv('select/2020-12-31_10.csv',index=False)
all_data[all_data['报告时间'] == '2021-12-31'].sort_values(by='10年平均ROE',ascending=False).to_csv('select/2021-12-31_10.csv',index=False)


pd_list = []
for file in os.listdir('temp'):
    try:
        data = pd.read_csv('temp/'+file)
        data.sort_index(ascending=False,inplace=True)
        data = data[['代码','名称','上市日期','报告时间','净资产收益率']]
        data['净资产收益率'] = data['净资产收益率'].astype(np.float64)
        data['5年平均ROE'] = data['净资产收益率'].rolling(5).mean()
        data['5年最低ROE'] = data['净资产收益率'].rolling(5).min()
        data = data[(data['5年平均ROE'] >= 20) & (data['5年最低ROE'] >= 15)]
        data = data.dropna()
        pd_list.append(data)
    except Exception as e:
        print('temp/'+file, str(e))

all_data = pd.concat(pd_list)
all_data[all_data['报告时间'] == '2010-12-31'].sort_values(by='5年平均ROE',ascending=False).to_csv('select/2010-12-31_5.csv',index=False)
all_data[all_data['报告时间'] == '2011-12-31'].sort_values(by='5年平均ROE',ascending=False).to_csv('select/2011-12-31_5.csv',index=False)
all_data[all_data['报告时间'] == '2012-12-31'].sort_values(by='5年平均ROE',ascending=False).to_csv('select/2012-12-31_5.csv',index=False)
all_data[all_data['报告时间'] == '2013-12-31'].sort_values(by='5年平均ROE',ascending=False).to_csv('select/2013-12-31_5.csv',index=False)
all_data[all_data['报告时间'] == '2014-12-31'].sort_values(by='5年平均ROE',ascending=False).to_csv('select/2014-12-31_5.csv',index=False)
all_data[all_data['报告时间'] == '2015-12-31'].sort_values(by='5年平均ROE',ascending=False).to_csv('select/2015-12-31_5.csv',index=False)
all_data[all_data['报告时间'] == '2016-12-31'].sort_values(by='5年平均ROE',ascending=False).to_csv('select/2016-12-31_5.csv',index=False)
all_data[all_data['报告时间'] == '2017-12-31'].sort_values(by='5年平均ROE',ascending=False).to_csv('select/2017-12-31_5.csv',index=False)
all_data[all_data['报告时间'] == '2018-12-31'].sort_values(by='5年平均ROE',ascending=False).to_csv('select/2018-12-31_5.csv',index=False)
all_data[all_data['报告时间'] == '2019-12-31'].sort_values(by='5年平均ROE',ascending=False).to_csv('select/2019-12-31_5.csv',index=False)
all_data[all_data['报告时间'] == '2020-12-31'].sort_values(by='5年平均ROE',ascending=False).to_csv('select/2020-12-31_5.csv',index=False)
all_data[all_data['报告时间'] == '2021-12-31'].sort_values(by='5年平均ROE',ascending=False).to_csv('select/2021-12-31_5.csv',index=False)
