import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

font_path = 'fonts/SimHei.ttf'
font_prop = FontProperties(fname=font_path)

def save_img(df,date_str):
    # 创建一个 Matplotlib 图像
    fig, ax = plt.subplots(figsize=(10, 1))  # 设置图片大小

    # 隐藏坐标轴
    ax.axis('tight')
    ax.axis('off')

    # 将 DataFrame 转换为表格并添加到图像中
    table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')

    # 设置表格样式
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.5, 1.5)  # 调整表格大小

    # 设置背景色和边框
    colors = ['#ccffcc','#008000']  # 浅绿色和深绿色
    header_color = '#40466e'
    row_colors = ['#f1f1f2', '#ffffff']
    edge_color = '#4d4d4d'

    for (i, key) in enumerate(table.get_celld().keys()):
        cell = table.get_celld()[key]
        cell.set_edgecolor(edge_color)
        if key[0] == 0:  # 标题行
            cell.set_facecolor(header_color)
            cell.set_text_props(color='w', weight='bold', fontproperties=font_prop)
        else:
            # 仅当 'Values' 列的值小于 'Threshold' 列的值时设置背景色
            row = key[0] - 1  # 数据行索引
            if df.loc[row, '最新价'] < df.loc[row, '市盈率估值买点'] and df.loc[row, '最新价'] < df.loc[row, '净利润估值买点']:
                cell.set_facecolor(colors[1])
            elif df.loc[row, '最新价'] < df.loc[row, '市盈率估值买点'] or df.loc[row, '最新价'] < df.loc[row, '净利润估值买点']:
                cell.set_facecolor(colors[0])
            else:
                cell.set_facecolor(row_colors[row % len(row_colors)])
            cell.set_text_props(color=edge_color, fontproperties=font_prop)

    # 保存图像为图片文件
    plt.savefig(f'static/{date_str}.png', bbox_inches='tight', pad_inches=0, dpi=300)

    # 显示图像
    plt.show()
