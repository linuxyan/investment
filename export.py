from datetime import datetime
import pandas as pd

current_date_str = datetime.now().strftime('%Y-%m-%d')
df = pd.read_pickle('data/day/last.pkl')

# 计算市盈率估值
df['市盈率估值'] = (df['市盈率(TTM)'] / (df['平均市盈率(5Y)(w)'])).round(2)

# 计算净利润估值
df['净利润估值'] = (df['总市值'] / (df['平均市盈率(5Y)(w)'] * 0.8 * df['fix_预测净利润(亿)(w)'] * 1e8)).round(2)

df['市盈率估值买点'] = df['最新价'] / df['市盈率估值'] * 0.5
df['净利润估值买点'] = df['最新价'] / df['净利润估值'] * 0.5

df['市盈率估值买点'] = df['市盈率估值买点'].astype(int)
df['净利润估值买点'] = df['净利润估值买点'].astype(int)

df['日期'] = current_date_str

# 显示结果
last_df = df[['日期', '股票名称', '市盈率估值', '净利润估值', '最新价', '市盈率估值买点', '净利润估值买点', 'date(w)', 'date(d)']].copy()
print(last_df)
last_df.to_pickle(f'data/export/export_{current_date_str}')
last_df.to_html('dataframe.html', index=False)


with open('dataframe.html', 'r', encoding='utf-8') as f:
    table_content = f.read()
    table_content = table_content.replace('border="1" class="dataframe"', 'class="stock-table"')


with open('index_template.html', 'r', encoding='utf-8') as f:
    index_content = f.read()


index_content = index_content.replace('temlpate_context', table_content).replace('Stock Table', current_date_str)
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(index_content)
