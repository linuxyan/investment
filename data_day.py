import datetime
import pandas as pd
import akshare as ak
from retry import retry
from config import BASIC_DATA_WEEKLY_CSV


"""
更新每日股票数据并返回包含最新信息的 DataFrame。

该函数从指定的基本数据文件中读取每周股票数据，获取每只股票的日数据，并将其与周数据合并。最终生成的 DataFrame 包含最新价格、市盈率、股息率、总市值、总股本及日期信息，并将结果保存为 pickle 文件。

返回:
    pd.DataFrame: 包含更新后的股票日数据的 DataFrame。
"""
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


"""
获取指定股票的日数据指标。

该函数通过调用阿尔法财经接口获取股票的日数据指标，包括基金份额、资产净值、股息率、市盈率和现价等信息。
在获取数据时，如果未找到指定指标，将抛出异常。函数会在发生异常时重试最多5次。

参数：
    symbol (str): 股票的代码，需添加前缀以符合接口要求。

返回：
    list: 包含现价、市盈率、股息率、总市值、基金份额和当前日期的列表。

异常：
    ValueError: 如果未找到指定的指标。
    Exception: 如果在重试后仍然失败，将抛出异常。
"""
@retry(delay=2, tries=5, logger=None)
def get_stock_day_data(symbol):
    try:
        # 获取股票日数据指标数据
        indicator_data = ak.stock_individual_spot_xq(symbol=add_prefix(symbol),token='84ee047de53c45257412fe452286f0b0fce68b9b')

        items = {
            '基金份额/总股本': 'equity_cap',
            '资产净值/总市值': 'market_cap',
            '股息率(TTM)': 'dividend_yield_ratio',
            '市盈率(TTM)': 'pe_ttm',
            '现价': 'last_price'
        }
        
        data = {}
        for item, key in items.items():
            value = indicator_data.loc[indicator_data['item'] == item, 'value']
            if not value.empty:
                data[key] = value.values[0]
            else:
                raise ValueError(f"指标 '{item}' 未找到")
        
        current_date = datetime.date.today().strftime('%Y-%m-%d')
        return [data['last_price'], data['pe_ttm'], data['dividend_yield_ratio'], 
                data['market_cap'], data['equity_cap'], current_date]
        
    except Exception as e:
        print(f"Error get_stock_day_data: {e}")
        raise Exception(f"Failed after 5 retries: {e}")


"""
根据给定的股票代码添加前缀。

该函数根据股票代码的前缀返回相应的市场前缀：
- 如果代码以 '60' 开头，返回 'SH' 前缀（上海证券市场）。
- 如果代码以 '00' 或 '30' 开头，返回 'SZ' 前缀（深圳证券市场）。
- 如果代码以 'hk' 开头，返回去掉前缀后的代码（香港市场）。
- 对于其他情况，返回原始代码。

参数:
    symbol (str): 股票代码。

返回:
    str: 带有市场前缀的股票代码。
"""
def add_prefix(symbol):
    if symbol.startswith('60'):
        return 'SH' + symbol
    elif symbol.startswith('00') or symbol.startswith('30'):
        return 'SZ' + symbol
    elif symbol.lower().startswith('hk'):
        return symbol[2:]
    else:
        return symbol


if __name__ == "__main__":
    stock_weekly_pd = day_data_update()
    print(stock_weekly_pd)
