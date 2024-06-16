from datetime import datetime, timedelta
import warnings
import akshare as ak
import pandas as pd
from retry import retry
from config import BASIC_DATA_CSV

warnings.simplefilter(action='ignore', category=FutureWarning)


def weekly_data_update() -> pd.DataFrame:
    """
    市盈率 ak.get_stock_indicator_data
    :return: 平均市盈率(5)(weekly), date(weekly)
    :rtype: pandas.DataFrame
    """
    basic_stock_pd = pd.read_csv(BASIC_DATA_CSV, dtype={'股票代码': str})
    column_names = basic_stock_pd.columns.tolist()
    basic_stock_list = basic_stock_pd.values.tolist()
    basic_stock_weekly = []
    for stock in basic_stock_list:
        print(f'Get weekly data : {stock[0:-1]}')
        pe_ttm_avg, pe_ttm_std, latest_date = get_stock_pettm_mean(symbol=stock[0])
        column_name, min_values = get_stock_net_profit(symbol=stock[0])
        stock += [pe_ttm_avg, pe_ttm_std, latest_date]
        stock += min_values
        basic_stock_weekly.append(stock)
    column_names += ['平均市盈率(5Y)(w)', '市盈率标准差(5Y)(w)', 'date(w)']
    column_names += column_name
    stock_weekly_pd = pd.DataFrame(basic_stock_weekly, columns=column_names)
    stock_weekly_pd.to_pickle('data/weekly/last.pkl')
    stock_weekly_pd.to_pickle(f'data/weekly/{latest_date}.pkl')
    return stock_weekly_pd


@retry(delay=2, tries=5, logger=None)
def get_stock_pettm_mean(symbol):
    try:
        # 获取股票指标数据
        indicator_data = ak.stock_a_indicator_lg(symbol=symbol)
        indicator_data.set_index('trade_date', inplace=True)
        today = datetime.today().date()

        # 计算五年前的日期
        five_years_ago = today - timedelta(days=5*365)

        # 提取最近五年的pe_ttm数据
        pe_ttm_data = indicator_data[indicator_data.index >= five_years_ago]['pe_ttm']
        pe_ttm_avg = pe_ttm_data.mean().round(2)
        pe_ttm_std = pe_ttm_data.std().round(2)
        latest_date = indicator_data.index.max()
        return pe_ttm_avg, pe_ttm_std, latest_date
    except Exception as e:
        print(f"Error occurred: {e}")
        raise Exception(f"Failed after 10 retries: {e}")


@retry(delay=2, tries=5, logger=None)
def get_stock_net_profit(symbol):
    try:
        # 获取股票指标数据
        indicator_data = ak.stock_profit_forecast_ths(symbol=symbol, indicator="预测年报净利润")

        max_year = indicator_data['年度'].max()
        min_value_for_max_year = float(indicator_data.loc[indicator_data['年度'] == max_year, '最小值'].values[0])
        column_name = '预测净利润(亿)(w)'

        # 平均三年后的预测净利润，如果业绩增速年化大于25，则修正为8折
        indicator_data = ak.stock_profit_forecast_ths(symbol=symbol, indicator="业绩预测详表-详细指标预测")
        net_profit_value = float(str(indicator_data.iloc[3, 3]).replace('亿',''))  # 最近一年实际净利润
        net_profit_value = float("{:.2f}".format(net_profit_value))

        # 三年后的净利润大于最近一年的实际净利润1.95倍(年化净利润增速25%) 1 * 1.25 * 1.25 * 1.25 = 1.95
        # 则修正净利润增速为20%
        min_value_for_max_year_fix = min_value_for_max_year
        if min_value_for_max_year / net_profit_value >= 1.95:
            min_value_for_max_year_fix = net_profit_value * 1.20 * 1.20 * 1.20  # 修正三年后的净利润

        return ['预测年份', column_name, 'fix_'+column_name], [max_year, min_value_for_max_year, min_value_for_max_year_fix]
    except Exception as e:
        print(f"Error occurred: {e}")
        raise Exception(f"Failed after 10 retries: {e}")


if __name__ == "__main__":
    today = datetime.now()
    if today.weekday() == 4:    # 周五
        stock_weekly_pd = weekly_data_update()
        print(stock_weekly_pd)
    else:
        print('not run.')


