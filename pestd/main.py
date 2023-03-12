from datetime import datetime

from finance_data import FinanceData

data = FinanceData()
# data.save_stock_basic()
# data.save_fina_indicator()                # 保存所有股票的roe 数据
# data.count_R15(2022)                      # 根据roe更新R15列表
# data.save_daily_basic(data.query_R15())   # 更新R15列表的日pe数据


curr_date = int(datetime.now().strftime('%m%d'))
if curr_date >= 501:
    R15_year = int(datetime.now().strftime('%Y'))
else:
    R15_year = int(datetime.now().strftime('%Y')) - 1

curr_R15 = data.query_R15(R15_year)

print(curr_R15)
