from pe_std import PeStd
import pandas as pd
from db_utils import DBManager
import tushare as ts


pro = ts.pro_api('a44e2a405b4b8abc8373f202480c3bfffdcaa4e7b3b5a35613d851cd')
df = pro.trade_cal(start_date='20180501', end_date='20230317',is_open='1')
trade_dates = df['cal_date'].values.tolist()
trade_dates.sort()

db = DBManager()
hold_stocks = pd.DataFrame(columns=['证券代码','证券简称','日期','收盘价','PE_TTM'])
hold_stocks_len = len(hold_stocks)
buy_sell_list = []

for trade_date in trade_dates:
    print(trade_date)
    trade_date_pe_std = PeStd(trade_date).count_pe_std()

    for _, hold in hold_stocks.iterrows():
        if hold['证券代码'] not in trade_date_pe_std['ts_code'].values.tolist():
            hold_stocks =hold_stocks[~hold_stocks['证券代码'].isin([hold['证券代码']])]
            stock_basic = db.get_daily_basic_last(ts_code=hold['证券代码'],trade_date=trade_date)
            buy_sell_list.append([trade_date,hold['证券简称'],stock_basic['close'],stock_basic['pe_ttm'],'卖出','R15剔除卖出'])
            print([trade_date,hold['证券简称'],stock_basic['close'],stock_basic['pe_ttm'],'卖出','R15剔除卖出'])


    sell_df = trade_date_pe_std.copy()
    sell_df = sell_df[(sell_df['pe_sell_ratio'] >=120 )]
    for _, sell in sell_df.iterrows():
        if sell['ts_code'] in hold_stocks['证券代码'].values.tolist():

            hold_stocks = hold_stocks[~hold_stocks['证券代码'].isin([sell['ts_code']])]

            buy_sell_list.append([trade_date,sell['name'],sell['close'],sell['pe_ttm'],'卖出','达到卖点'])

            print([trade_date,sell['name'],sell['close'],sell['pe_ttm'],'卖出','达到卖点'])


    buy_data = trade_date_pe_std.copy()
    buy_data = buy_data[(buy_data['pe_buy_ratio'] < 2)]
    for _, buy in buy_data.iterrows():
        if buy['ts_code'] not in hold_stocks['证券代码'].values.tolist():

            temp_df = pd.DataFrame({'证券代码':buy['ts_code'],'证券简称':buy['name'],'日期':buy['trade_date'],'收盘价':buy['close'],'PE_TTM':buy['pe_ttm']},index=[0])

            hold_stocks = pd.concat([hold_stocks,temp_df], ignore_index=True)

            buy_sell_list.append([trade_date,buy['name'],buy['close'],buy['pe_ttm'],'买入','达到买点'])

            print([trade_date,buy['name'],buy['close'],buy['pe_ttm'],'买入','达到买点'])

    if hold_stocks_len != len(hold_stocks):
        hold_stocks.reset_index(drop=True, inplace=True)
        print(hold_stocks)
        hold_stocks_len = len(hold_stocks)

buy_sell_df = pd.DataFrame(buy_sell_list,columns=['日期','证券简称','收盘价','PE_TTM','操作','原因'])
buy_sell_df.to_csv('buy_sell.csv', encoding='utf_8_sig')


