from datetime import datetime
import os
import numpy as np
import pandas as pd
from save_img import save_img
from wechat import push_content

current_date_str = datetime.now().strftime('%Y-%m-%d')
df = pd.read_pickle('data/day/last.pkl')

# 合理市盈率： ((最近五年的平均市盈率-最近五年的市盈率标准差) + 最近五年的平均市盈率) / 2
df['合理市盈率'] = ((df['平均市盈率(5Y)(w)'] - df['市盈率标准差(5Y)(w)']) + df['平均市盈率(5Y)(w)']).round(2) / 2 

# 计算市盈率估值
df['市盈率估值'] = (df['市盈率(TTM)'] / df['合理市盈率']).round(2)
# 三年后的市盈率为当前合理市盈率的8折。计算净利润估值
df['净利润估值'] = (df['总市值'] / (df['合理市盈率'] * 0.8 * df['fix_预测净利润(亿)(w)'] * 1e8)).round(2)


# 如果合理市盈率大于20，则合理股价的5折为买点，如果合理市盈率小于20，则6折为买点。
df['市盈率估值买点'] = np.where(df['合理市盈率'] >= 20, df['最新价'] / df['市盈率估值'] * 0.5, df['最新价'] / df['市盈率估值'] * 0.6)

df['净利润估值买点'] = np.where(df['合理市盈率'] >= 20, df['最新价'] / df['净利润估值'] * 0.5, df['最新价'] / df['净利润估值'] * 0.6)

df['市盈率估值买点'] = df['市盈率估值买点'].astype(int)
df['净利润估值买点'] = df['净利润估值买点'].astype(int)

df['日期'] = current_date_str

print(df)
df.to_pickle(f'data/export/export_{current_date_str}.pkl')

date_w = df['date(w)'].apply(lambda x: x.strftime('%Y-%m-%d')).copy()
date_d = df['date(d)'].copy()

date_w = ' '.join(date_w.unique())
date_d = ' '.join(date_d.unique())


# 显示结果
last_df = df[['日期', '股票名称', '市盈率估值', '净利润估值', '最新价', '市盈率估值买点', '净利润估值买点', '市盈率(TTM)', '合理市盈率','股息率(TTM)','fix_预测净利润(亿)(w)']].copy()
last_df = last_df.rename(columns={'fix_预测净利润(亿)(w)': '预测净利润(3Y)'})
print(last_df)
last_df.to_html('dataframe.html', index=False)


with open('dataframe.html', 'r', encoding='utf-8') as f: table_content = f.read()
table_content = table_content.replace('border="1" class="dataframe"', 'class="stock-table"')

with open('index_template.html', 'r', encoding='utf-8') as f: index_content = f.read()

os.remove('dataframe.html')
index_content = index_content.replace('temlpate_context', table_content).replace('Stock Table', current_date_str)
index_content = index_content.replace('date_w', date_w).replace('date_d', date_d)
with open('index.html', 'w', encoding='utf-8') as f: f.write(index_content)

name_list_str = ' | '.join(last_df['股票名称'].tolist())
save_img(last_df,current_date_str)
push_content(current_date_str, name_list_str)