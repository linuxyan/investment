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

            print(index, '/', stock_basic_df.shape[0], stock['ts_code'], stock['name'])

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
                fina_indicator_stock.append(stock_df)
                offset += limit
                time.sleep(0.35)
                if len(stock_df) < limit:
                    break

            fina_indicator_stock = pd.concat(fina_indicator_stock)
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

    def save_db():
        pass
