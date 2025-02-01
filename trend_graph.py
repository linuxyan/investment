import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.font_manager import FontProperties

'''
绘制每只股票的最新价和买点价的长期趋势图
'''

font_path = 'fonts/SimHei.ttf'
font_prop = FontProperties(fname=font_path)

# 设置数据目录
data_dir = 'data/export/'

# 获取所有以 'export' 开头的 .pkl 文件
pkl_files = [f for f in os.listdir(data_dir) if f.startswith('export') and f.endswith('.pkl')]

# 提取所需的数据并合并
all_data = []

for file in pkl_files:
    # 读取 pkl 文件
    df = pd.read_pickle(os.path.join(data_dir, file))
    
    # 选择需要的列
    if '股票名称' in df.columns and '日期' in df.columns and '最新价' in df.columns and '市盈率估值买点' in df.columns and '净利润估值买点' in df.columns:
        df = df[['股票代码','股票名称', '日期', '最新价', '市盈率估值买点', '净利润估值买点']]
        all_data.append(df)

# 合并所有数据
merged_data = pd.concat(all_data)

# 确保日期列是 datetime 类型
merged_data['日期'] = pd.to_datetime(merged_data['日期'])

# 按股票代码分组，按日期排序
merged_data = merged_data.sort_values(by=['股票代码','股票名称', '日期'])

# 绘制每只股票的变化趋势
stock_codes = merged_data['股票代码'].unique()

for stock_code in stock_codes:
    stock_data = merged_data[merged_data['股票代码'] == stock_code]

    stock_name = stock_data['股票名称'].unique()[0]

    json_pd = stock_data[['日期','股票名称','最新价','市盈率估值买点','净利润估值买点']].copy()
    json_pd['日期'] = pd.to_datetime(json_pd['日期']).dt.strftime('%Y-%m-%d')
    # 转换为JSON格式
    json_data = json_pd.to_json(orient='records', force_ascii=False, indent=4)
    
    # 保存到文件
    with open(f'trend_graph/{stock_code}.json', 'w', encoding='utf-8') as f:
        f.write(json_data)

    plt.figure(figsize=(15, 6))
    plt.plot(stock_data['日期'], stock_data['最新价'], label='最新价', marker='', linestyle='-')
    plt.plot(stock_data['日期'], stock_data['市盈率估值买点'], label='市盈率估值买点', marker='', linestyle='-')
    plt.plot(stock_data['日期'], stock_data['净利润估值买点'], label='净利润估值买点', marker='', linestyle='-')

    # 设置图表标题和标签
    plt.title(f'{stock_name} - 价格买卖点变化趋势', fontproperties=font_prop)
    plt.xlabel('日期', fontproperties=font_prop)
    plt.ylabel('价格', fontproperties=font_prop)
    plt.legend(prop=font_prop)
    plt.grid(True)

    # 显示图表
    # 设置 x 轴日期格式和间隔
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))  # 每5天显示一个刻度
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # 自定义日期格式
    plt.xticks(rotation=45, fontproperties=font_prop)
    plt.tight_layout()

    plt.savefig(f'trend_graph/{stock_name}.png', bbox_inches='tight', pad_inches=0, dpi=300)

