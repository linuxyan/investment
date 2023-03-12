import time
from datetime import datetime

import pandas as pd
import tushare as ts
from db_utils import DBManager


class FinanceData:
    def __init__(self) -> None:
        self.list_year = 5
        self.pro = ts.pro_api('a44e2a405b4b8abc8373f202480c3bfffdcaa4e7b3b5a35613d851cd')
        self.db = DBManager()
        self.slee_time = 0.35

    def save_stock_basic(self):
        while True:
            all_stocks_df = self.pro.stock_basic(
                list_status="L", fields=["ts_code", "name", "area", "industry", "list_date"]
            )
            if not all_stocks_df.empty:
                break
        all_stocks_df.reset_index(drop=True, inplace=True)
        all_stocks_df.to_sql('stock_basic', con=self.db.engine, index=False, if_exists='replace')

    def save_fina_indicator(self, full=False):
        list_date_end = str(int(datetime.now().strftime('%Y')) - self.list_year) + '1231'
        stock_basic_df = self.db.get_stock_basic(list_date_end=list_date_end)

        fina_indicator_list = []
        for index, stock in stock_basic_df.iterrows():

            start_date = stock['list_date']
            if full is False:
                fina_indicator_last = self.db.get_fina_indicator_last(ts_code=stock['ts_code'])
                if fina_indicator_last:
                    start_date = fina_indicator_last['end_date']

            fina_indicator_stock = []
            limit, offset = 60, 0
            while True:
                stock_df = self.pro.fina_indicator(
                    ts_code=stock['ts_code'],
                    start_date=int(start_date),
                    limit=limit,
                    offset=offset,
                    update_flag=1,
                    fields=[
                        "ts_code",
                        "ann_date",
                        "end_date",
                        "roe_waa",
                        "netprofit_yoy",
                        "debt_to_assets",
                        "netprofit_margin",
                        "grossprofit_margin",
                    ],
                )
                print(
                    index,
                    '/',
                    stock_basic_df.shape[0],
                    stock['ts_code'],
                    stock['name'],
                    start_date,
                    limit,
                    offset,
                    len(stock_df),
                )
                time.sleep(self.slee_time)
                if not stock_df.empty:
                    fina_indicator_stock.append(stock_df)
                    offset += limit - 1  # -1 防止只有120条数据卡入死循环
                    if len(stock_df) < limit:
                        break
            try:
                fina_indicator_stock = pd.concat(fina_indicator_stock)
            except Exception as e:
                print(fina_indicator_stock)
            fina_indicator_stock = fina_indicator_stock[fina_indicator_stock.end_date.str[-4:] == '1231']
            fina_indicator_stock.drop_duplicates(
                subset=['ts_code', 'ann_date', 'end_date', 'roe_waa'], keep='first', inplace=True
            )

            if full is False:
                fina_indicator_stock = fina_indicator_stock[fina_indicator_stock['end_date'] != start_date]

            if not fina_indicator_stock.empty:
                fina_indicator_list.append(fina_indicator_stock)

        if len(fina_indicator_list) > 0:
            fina_indicator_df = pd.concat(fina_indicator_list)

            if full:
                fina_indicator_df.to_sql('fina_indicator', con=self.db.engine, index=False, if_exists='replace')
            else:
                fina_indicator_df.to_sql('fina_indicator', con=self.db.engine, index=False, if_exists='append')

    def count_R15(self, year):
        r15_pd = self.db.count_r15(year)
        if r15_pd.empty:
            print(year, 'R15 is Null')
            return None

        r15_pd['year'] = year
        r15_pd['start_date'] = int(str(year) + '0501')
        r15_pd['end_date'] = int(str(year + 1) + '0430')
        r15_pd = r15_pd.drop(labels='net_std', axis=1)
        debt_to_assets_df = self.db.get_fina_indicator_debt_to_assets(
            ts_code_list=r15_pd['ts_code'].values.tolist(), end_date=int(str(year - 1) + '1231')
        )
        r15_pd = pd.merge(r15_pd, debt_to_assets_df)
        self.db.drop_r15(year)
        r15_pd.to_sql('r15', con=self.db.engine, index=False, if_exists='append')

    def query_R15(self, year=None):
        return self.db.query_r15(year)

    def save_daily_basic(self, R15_df, full=False):

        R15_df.drop_duplicates(subset=['ts_code'], keep='first', inplace=True)
        stock_basic = self.db.get_stock_basic()
        R15_df = pd.merge(R15_df, stock_basic)

        daily_basic_list = []
        for index, stock in R15_df.iterrows():

            start_date = stock['list_date']
            if full is False:
                daily_basic_last = self.db.get_daily_basic_last(ts_code=stock['ts_code'])
                if daily_basic_last:
                    start_date = daily_basic_last['trade_date']

            while True:
                stock_df = self.pro.daily_basic(
                    ts_code=stock['ts_code'],
                    start_date=int(start_date),
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
                print(index, '/', R15_df.shape[0], stock['ts_code'], stock['name'], len(stock_df))
                time.sleep(self.slee_time)
                if not stock_df.empty:
                    if full is False:
                        stock_df = stock_df[stock_df['trade_date'] != start_date]
                    if not stock_df.empty:
                        daily_basic_list.append(stock_df)
                    break

        if len(daily_basic_list) > 0:
            daily_basic_df = pd.concat(daily_basic_list)

            if full:
                daily_basic_df.to_sql('daily_basic', con=self.db.engine, index=False, if_exists='replace')
            else:
                daily_basic_df.to_sql('daily_basic', con=self.db.engine, index=False, if_exists='append')
