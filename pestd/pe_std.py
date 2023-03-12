import datetime

import pandas as pd
from db_utils import DBManager


class PeStd:
    def __init__(self, end_date) -> None:
        self.db = DBManager()
        self.std_multiple_init = 1.5  # 标准差倍数
        self.year_list = [3, 5]  # 采样年数
        self.end_date = end_date

    def get_date_range(self, year):
        start_date = datetime.datetime.strptime(str(self.end_date), '%Y%m%d') - datetime.timedelta(weeks=(year * 52))
        return int(start_date.strftime('%Y%m%d')), int(self.end_date.strftime('%Y%m%d'))

    def get_R15_df(self):
        curr_date = int(self.end_date.strftime('%m%d'))
        if curr_date >= 501:
            R15_year = int(datetime.now().strftime('%Y'))
        else:
            R15_year = int(datetime.now().strftime('%Y')) - 1
        R15_df = self.db.query_r15(R15_year)
        return R15_df

    def count_pe_std(self):
        R15_df = self.get_R15_df()
        for _, row in R15_df.iterrows():
            pass
            # for year in year_list:
