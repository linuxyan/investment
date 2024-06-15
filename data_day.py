import datetime
import pandas as pd
import akshare as ak
from retry import retry
from config import BASIC_DATA_WEEKLY_CSV


def day_data_update() -> pd.DataFrame:
    basic_stock_weekly_pd = pd.read_pickle(BASIC_DATA_WEEKLY_CSV)
    current_date = datetime.date.today().strftime('%Y-%m-%d')
    column_names = basic_stock_weekly_pd.columns.tolist()
    basic_stock_weekly_list = basic_stock_weekly_pd.values.tolist()
    basic_stock_day = []
    for stock in basic_stock_weekly_list:
        print(f'Get day data : {stock[0:2]}')
        stock += get_stock_day_data(symbol=stock[0])
        basic_stock_day.append(stock)
    column_names += ['最新价', '市盈率(TTM)', '股息率(TTM)', '总市值', '总股本', 'date(d)']
    stock_day_pd = pd.DataFrame(basic_stock_day, columns=column_names)
    stock_day_pd.to_pickle('data/day/last.pkl')
    stock_day_pd.to_pickle(f'data/day/{current_date}.pkl')
    return stock_day_pd


@retry(delay=2, tries=5, logger=None)
def get_stock_day_data(symbol):
    try:
        # 获取股票日数据指标数据
        indicator_data = ak.stock_individual_spot_xq(symbol=add_prefix(symbol))

        equity_cap = indicator_data.loc[indicator_data['item'] == '基金份额/总股本', 'value'].values[0]
        market_cap = indicator_data.loc[indicator_data['item'] == '资产净值/总市值', 'value'].values[0]
        dividend_yield_ratio = indicator_data.loc[indicator_data['item'] == '股息率(TTM)', 'value'].values[0]
        pe_ttm = indicator_data.loc[indicator_data['item'] == '市盈率(TTM)', 'value'].values[0]
        last_price = indicator_data.loc[indicator_data['item'] == '现价', 'value'].values[0]
        current_date = datetime.date.today().strftime('%Y-%m-%d')

        return [last_price, pe_ttm, dividend_yield_ratio, market_cap, equity_cap, current_date]
    except Exception as e:
        print(f"Error get_stock_day_data: {e}")
        raise Exception(f"Failed after 5 retries: {e}")


def add_prefix(symbol):
    if symbol.startswith('60'):
        return 'SH' + symbol
    elif symbol.startswith('00') or symbol.startswith('30'):
        return 'SZ' + symbol
    else:
        return symbol


if __name__ == "__main__":
    stock_weekly_pd = day_data_update()
    print(stock_weekly_pd)
