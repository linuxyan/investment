import pandas as pd

# 给定的数据，每行作为一个元组
data = [
    ('600519', '贵州茅台', 1),
    ('600436', '片仔癀', 1),
    ('000858', '五粮液', 1),
    ('603288', '海天味业', 1),
    ('600887', '伊利股份', 1),
    ('600036', '招商银行', 1),
    ('000895', '双汇发展', 1),
    ('000568', '泸州老窖', 1),
    ('600329', '达仁堂', 1),
    ('600612', '老凤祥', 1),
    ('600600', '青岛啤酒', 1),
    ('000333', '美的集团', 1),
    ('300760', '迈瑞医疗', 1.5)
]

# 转换为 Pandas DataFrame
df = pd.DataFrame(data, columns=['股票代码', '股票名称', '市盈率标准差倍数'])

# 保存为 CSV 文件
df.to_csv('data/stocks_data.csv', index=False)
df.to_pickle('data/stocks_data.pkl')

# 设置样式函数，大于1的行底色为绿色并设置边框
def highlight_high_std(val):
    if isinstance(val, (int, float)):
        color = 'lightgreen' if val > 1 else ''
        return f'background-color: {color}; border: 1px solid black;'
    else:
        return ''

# 应用样式到 DataFrame 的每行
# styled_df = df.style.applymap(highlight_high_std, subset=['市盈率标准差倍数'])
styled_df = df.style.apply(lambda x: [highlight_high_std(val) for val in x], axis=1)

# 将带有样式的 DataFrame 转换为 HTML 表格，并保存为文件
html_table = styled_df.to_html(index=False)

# 或者保存为 HTML 文件
with open('stocks_data.html', 'w') as f:
    f.write(html_table)