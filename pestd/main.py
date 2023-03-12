from datetime import datetime

from finance_data import FinanceData

data = FinanceData()
# data.save_stock_basic()
# data.save_fina_indicator()
# data.count_R15(2022)
# data.save_daily_basic(data.query_R15())   # 更新日pe数据


curr_date = int(datetime.now().strftime('%m%d'))
if curr_date >= 501:
    R15_year = int(datetime.now().strftime('%Y'))
else:
    R15_year = int(datetime.now().strftime('%Y')) - 1

curr_R15 = data.query_R15(R15_year)

print(curr_R15)
