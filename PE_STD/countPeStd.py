import pandas as pd
import numpy as np
import datetime

R15 = pd.read_csv('2022_R15.csv')
increase_ratio = 0.12  # 每年业绩增长比例(业绩增长+分红率)
std_multiple_init = 1.25  # 标准差倍数
year_list = [3, 5]  # 采样年数
end_date = datetime.datetime.now()
# end_date = datetime.datetime.strptime('20221031','%Y%m%d')


data = []
for _, row in R15.iterrows():
    code_data = pd.read_csv('data/%s_pe.csv' % row['证券代码'])
    finance_data = pd.read_csv('data/%s_finance.csv' % row['证券代码']).head(5)

    liab_ratio = round(finance_data['负债率'].mean(), 2)  # 负债率
    dividend_ratio = round(finance_data['分红率'].mean(), 2)  # 分红率 利润是否为真
    cash_div = round(finance_data['每股分红'].mean(), 2)  # 每股分红
    roe_mean = round(finance_data['roe'].mean(), 2)

    std_multiple = std_multiple_init
    if liab_ratio > 45:  # # 近五年负债率大于45 标准差增加0.25
        std_multiple += 0.25
    if dividend_ratio < 30:  # 近五年分红率小于30 标准差增加0.25
        std_multiple += 0.25
    if roe_mean < 25:  # 近五年roe小于30 标准差增加0.25
        std_multiple += 0.25

    code_data = code_data[code_data['trade_date'] <= int(end_date.strftime('%Y%m%d'))]
    code_data_last = code_data[code_data['trade_date'] == code_data['trade_date'].max()]
    pe_ttm_last = code_data_last['pe_ttm'].iloc[0]
    close_last = code_data_last['close'].iloc[0]
    dv_ttm = code_data_last['dv_ttm'].iloc[0]
    dv_5_ttm = round(cash_div / close_last * 100, 2)
    code_data_std = [
        row['证券代码'],
        row['证券简称'],
        row['跟踪时间'],
        code_data_last['trade_date'].iloc[0],
        close_last,
        dv_ttm,
        dv_5_ttm,
        pe_ttm_last,
    ]
    fix_data = None
    for year in year_list:
        start_date = end_date - datetime.timedelta(weeks=(year * 52))
        year_data = code_data[code_data['trade_date'] >= int(start_date.strftime('%Y%m%d'))]
        pettm_mean = round(year_data['pe_ttm'].mean(), 2)
        pettm_std = round(year_data['pe_ttm'].std() * std_multiple, 2)

        if (pettm_mean - pettm_std) <= 0:
            print('fix %s %s std()' % (row['证券代码'], row['证券简称']))
            pettm_std = pettm_mean * 0.75
            fix_data = '修正标准差'

        pe_limit_low = pettm_mean - pettm_std
        pe_limit_up = pettm_mean + pettm_std

        # if pe_limit_low >=45:   # 长期高PE运行的股票，估值范围打7折。
        #     pe_limit_low = (pettm_mean - pettm_std) * 0.7
        #     pe_limit_up = (pettm_mean + pettm_std) * 0.7
        #     fix_data = '修正估值范围'

        pe_buy_ratio = int((pe_ttm_last / pe_limit_low - 1) * 100)
        pe_sell_ratio = int(pe_ttm_last / pe_limit_up * 100)
        mettm_limits = str(round(pe_limit_low, 2)) + '~' + str(round(pe_limit_up, 2))
        code_data_std += [pe_buy_ratio, pe_sell_ratio, pettm_mean, pettm_std, mettm_limits]

    code_data_std += [fix_data, std_multiple, cash_div, dividend_ratio, liab_ratio, roe_mean]
    data.append(code_data_std)

data = pd.DataFrame(
    data,
    columns=[
        '证券代码',
        '证券简称',
        '跟踪时间',
        '日期',
        '收盘价',
        '股息率',
        '五年股息率',
        'PE_TTM',
        '三年估值范围买点比例',
        '三年估值范围卖点比例',
        '三年PE_TTM均值',
        '三年PE_TTM标准差',
        '三年估值范围',
        '五年估值范围买点比例',
        '五年估值范围卖点比例',
        '五年PE_TTM均值',
        '五年PE_TTM标准差',
        '五年估值范围',
        '数据修正',
        '标准差倍数',
        '五年平均每股分红',
        '五年平均分红率',
        '五年平均负债率',
        '五年ROE',
    ],
)

data['距离买点%'] = np.round(data[['三年估值范围买点比例', '五年估值范围买点比例']].mean(axis=1), 2)
data['距离卖点%'] = np.round(data[['三年估值范围卖点比例', '五年估值范围卖点比例']].mean(axis=1), 2)
data = data[
    [
        '证券代码',
        '证券简称',
        '跟踪时间',
        '日期',
        '收盘价',
        '股息率',
        '五年股息率',
        'PE_TTM',
        '距离买点%',
        '距离卖点%',
        '五年ROE',
        '三年估值范围',
        '五年估值范围',
        '数据修正',
        '标准差倍数',
        '五年平均每股分红',
        '五年平均分红率',
        '五年平均负债率',
    ]
]
data.sort_values("距离买点%", inplace=True)
data['距离买点%'] = data['距离买点%'].astype(str) + '%'
data['距离卖点%'] = data['距离卖点%'].astype(str) + '%'
data.reset_index(drop=True, inplace=True)
data.to_csv('R15_%s_std.csv' % str(end_date.strftime('%Y%m%d')), encoding='utf_8_sig')
