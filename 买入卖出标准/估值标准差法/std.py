import pandas as pd
import datetime

R15 = pd.read_csv('2022_R15.csv')
hold_year = 3  # 持有时间
increase_ratio = 0.12  # 每年业绩增长比例(业绩增长+分红率)
std_multiple = 1  # 标准差倍数
year_list = [3, 5, 10]  # 采样年数

data = []
for _, row in R15.iterrows():
    code = str(row['证券代码']).split('.')[1].lower() + str(row['证券代码']).split('.')[0]
    code_data = pd.read_csv('data/%s.csv' % code)
    code_data_last = code_data[code_data['date'] == code_data['date'].max()]
    code_data_std = [row['证券代码'], row['证券简称'], code_data_last['date'].iloc[0], code_data_last['pe_ttm'].iloc[0]]
    for year in year_list:
        start_date = datetime.datetime.now() - datetime.timedelta(weeks=(year * 52))
        start_date_str = start_date.strftime('%Y-%m-%d')
        year_data = code_data[code_data['date'] >= start_date_str]
        pettm_mean = round(year_data['pe_ttm'].mean(), 2)
        pettm_std = round(year_data['pe_ttm'].std() * std_multiple, 2)

        # 业绩收益 = 1 + (年理论收益(increase_ratio) * 持有年数(hold_year))
        # 估值收益 = (N年平均估值 + N年估值标准差) / (N年平均估值 - N年估值标准差)
        # 总持有收益 = (业绩收益 * 估值收益 -1) * 100
        theory_profit = int(
            (
                (1 + (hold_year * increase_ratio))
                * (round(pettm_mean + pettm_std, 2) / round(pettm_mean - pettm_std, 2))
                - 1
            )
            * 100
        )
        mettm_limits = str(round(pettm_mean - pettm_std, 2)) + '~' + str(round(pettm_mean + pettm_std, 2))
        code_data_std += [pettm_mean, pettm_std, mettm_limits, str(theory_profit) + '%']

    data.append(code_data_std)

data = pd.DataFrame(
    data,
    columns=[
        '证券代码',
        '证券简称',
        '日期',
        'PE_TTM',
        '三年PE_TTM均值',
        '三年PE_TTM标准差',
        '三年估值范围',
        '三年理想收益',
        '五年PE_TTM均值',
        '五年PE_TTM标准差',
        '五年估值范围',
        '五年理想收益',
        '十年PE_TTM均值',
        '十年PE_TTM标准差',
        '十年估值范围',
        '十年理想收益',
    ],
)

data = data[
    [
        '证券代码',
        '证券简称',
        '日期',
        'PE_TTM',
        '三年估值范围',
        '三年理想收益',
        '五年估值范围',
        '五年理想收益',
        '十年估值范围',
        '十年理想收益',
        '三年PE_TTM均值',
        '三年PE_TTM标准差',
        '五年PE_TTM均值',
        '五年PE_TTM标准差',
        '十年PE_TTM均值',
        '十年PE_TTM标准差',
    ]
]
data.to_csv('R15_1_std.csv', index=False, encoding='utf_8_sig')
