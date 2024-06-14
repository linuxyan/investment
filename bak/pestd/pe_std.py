import datetime
from statistics import mean

import pandas as pd
from db_utils import DBManager


class PeStd:
    def __init__(self, end_date) -> None:
        self.db = DBManager()
        self.std_multiple = 1.5  # 标准差倍数
        self.year_list = [3, 5]  # 采样年数
        self.end_date = datetime.datetime.strptime(str(end_date), '%Y%m%d')

    def get_date_range(self, year):
        start_date = self.end_date - datetime.timedelta(weeks=(year * 52))
        return int(start_date.strftime('%Y%m%d')), int(self.end_date.strftime('%Y%m%d'))

    def get_R15_df(self):
        curr_date = int(self.end_date.strftime('%m%d'))
        if curr_date >= 501:
            R15_year = int(self.end_date.strftime('%Y'))
        else:
            R15_year = int(self.end_date.strftime('%Y')) - 1
        R15_df = self.db.query_r15(R15_year)
        return R15_df

    def count_pe_std(self):
        R15_df = self.get_R15_df()

        R15_pe_std = []
        for _, row in R15_df.iterrows():

            stock_basic_last = self.db.get_daily_basic_last(
                row['ts_code'], trade_date=int(self.end_date.strftime('%Y%m%d'))
            )
            trade_date_last = stock_basic_last['trade_date']
            pe_ttm_last = stock_basic_last['pe_ttm']
            close_last = stock_basic_last['close']

            code_data_std = [trade_date_last, row['ts_code'],row['name'], close_last, pe_ttm_last]

            pe_limit_low_list, pe_limit_up_list= [], []
            for year in self.year_list:
                start_date, end_date = self.get_date_range(year)

                stock_basic = self.db.get_daily_basic_ts_code(row['ts_code'], start_date, end_date)
                stock_basic_last = stock_basic[stock_basic['trade_date'] == stock_basic['trade_date'].max()]
                pettm_mean = round(stock_basic['pe_ttm'].mean(), 2)
                pettm_std = round(stock_basic['pe_ttm'].std() * self.std_multiple, 2)
                pe_limit_low = pettm_mean - pettm_std
                pe_limit_up = pettm_mean + pettm_std
                pe_limit_low_list.append(pe_limit_low)
                pe_limit_up_list.append(pe_limit_up)

            pe_limit_low_mean = mean(pe_limit_low_list)
            pe_limit_up_mean = mean(pe_limit_up_list)

            try:
                pe_buy_ratio = int((pe_ttm_last / pe_limit_low_mean - 1) * 100)
                pe_sell_ratio = int(pe_ttm_last / pe_limit_up_mean * 100)
                pettm_limits = str(round(pe_limit_low_mean, 2)) + '~' + str(round(pe_limit_up_mean, 2))
                code_data_std += [pe_buy_ratio, pe_sell_ratio, pettm_limits]
                code_data_std.append(row['debt_to_assets'])
                R15_pe_std.append(code_data_std)
            except Exception:
                print(row['ts_code'], pe_ttm_last, pe_limit_low_mean, pe_limit_up_mean)

        R15_pe_std_df = pd.DataFrame(R15_pe_std, columns=['trade_date','ts_code', 'name', 'close', 'pe_ttm', 'pe_buy_ratio', 'pe_sell_ratio', 'pettm_limits','debt_to_assets'])
        R15_pe_std_df.sort_values("pe_buy_ratio", inplace=True)
        R15_pe_std_df.reset_index(drop=True, inplace=True)

        self.db.drop_pe_std_history(trade_date=int(self.end_date.strftime('%Y%m%d')))
        R15_pe_std_df.to_sql('pe_std_history', self.db.engine,index=False, if_exists='append')
        return R15_pe_std_df
        

        # select ts_code,name,count(ts_code) from r15 where year >= 2017 and year <= 2020 GROUP BY ts_code HAVING count(ts_code) >= 4 ORDER BY count(ts_code) desc;