import akshare as ak
import datetime

current_date = datetime.date.today()
ten_years_ago = current_date - datetime.timedelta(days=365 * 10)

print(ten_years_ago)

stock_a_indicator_lg_df = ak.stock_a_indicator_lg(symbol="600519")
pe_ttm_df = stock_a_indicator_lg_df[stock_a_indicator_lg_df['trade_date'] >= ten_years_ago]

pe_ttm_df.to_pickle('data/600519_data.pkl')


# print(pe_ttm_df.head(10))
# print(pe_ttm_df.tail(20))

# # pe_ttm_mean = min(pe_ttm_df['pe_ttm'].mean(),pe_ttm_df['pe_ttm'].median())
# pe_ttm_mean = pe_ttm_df['pe_ttm'].mean()
# pe_ttm_std = pe_ttm_df['pe_ttm'].std()
# pe_ttm_last = pe_ttm_df.iloc[-1]['pe_ttm']

# pe_ttm_min = pe_ttm_mean-pe_ttm_std

# print(pe_ttm_mean, pe_ttm_std, pe_ttm_last, pe_ttm_min)

# aa = pe_ttm_df[pe_ttm_df['pe_ttm'] <= pe_ttm_min]

# print(aa.tail(50))