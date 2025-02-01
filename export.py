from datetime import datetime
import json
import numpy as np
import pandas as pd
from save_img import save_img

current_date_str = datetime.now().strftime("%Y-%m-%d")
df = pd.read_pickle("data/day/last.pkl")

# 合理市盈率： ((最近五年的平均市盈率-最近五年的市盈率标准差) + 最近五年的平均市盈率) / 2
df["合理市盈率"] = (
    (df["平均市盈率(5Y)(w)"] - df["市盈率标准差(5Y)(w)"]) + df["平均市盈率(5Y)(w)"]
).round(2) / 2

# 计算市盈率估值
df["市盈率估值"] = (df["市盈率(TTM)"] / df["合理市盈率"]).round(2)
# 三年后的市盈率为当前合理市盈率的8折。计算净利润估值
df["净利润估值"] = (
    df["总市值"] / (df["合理市盈率"] * 0.8 * df["fix_预测净利润(亿)(w)"] * 1e8)
).round(2)


# 如果合理市盈率大于20，则合理股价的5折为买点，如果合理市盈率小于20，则6折为买点。
df["市盈率估值买点"] = np.where(
    df["合理市盈率"] >= 20,
    df["最新价"] / df["市盈率估值"] * 0.5,
    df["最新价"] / df["市盈率估值"] * 0.6,
)

df["净利润估值买点"] = np.where(
    df["合理市盈率"] >= 20,
    df["最新价"] / df["净利润估值"] * 0.5,
    df["最新价"] / df["净利润估值"] * 0.6,
)

df["市盈率估值买点"] = df["市盈率估值买点"].astype(int)
df["净利润估值买点"] = df["净利润估值买点"].astype(int)

df["日期"] = current_date_str

print(df)
df.to_pickle(f"data/export/export_{current_date_str}.pkl")

date_w = df["date(w)"].apply(lambda x: x.strftime("%Y-%m-%d")).copy()
date_d = df["date(d)"].copy()

date_w = " ".join(date_w.unique())
date_d = " ".join(date_d.unique())

last_date = {"date_w": date_w, "date_d": date_d}

df["市盈率估值买点%"] = ((df["最新价"] / df["市盈率估值买点"] - 1) * 100).astype(int)
df["净利润估值买点%"] = ((df["最新价"] / df["净利润估值买点"] - 1) * 100).astype(int)
# 合并为新的列
df["现价/买点%"] = (
    df["市盈率估值买点%"].astype(str) + "|" + df["净利润估值买点%"].astype(str)
)


# 显示结果
last_df = df[
    [
        "日期",
        "股票代码",
        "股票名称",
        "市盈率估值",
        "净利润估值",
        "最新价",
        "市盈率估值买点",
        "净利润估值买点",
        "现价/买点%",
        "市盈率(TTM)",
        "合理市盈率",
        "股息率(TTM)",
        "fix_预测净利润(亿)(w)",
    ]
].copy()
last_df = last_df.rename(columns={"fix_预测净利润(亿)(w)": "预测净利润(3Y)"})

last_df["日期"] = pd.to_datetime(last_df["日期"]).dt.strftime("%Y-%m-%d")
# 转换为JSON格式
json_data = last_df.to_json(orient="records", force_ascii=False, indent=4)

# 保存到文件
with open(f"trend_graph/last.json", "w", encoding="utf-8") as f:
    f.write(json_data)

with open('trend_graph/last_date.json', 'w', encoding='utf-8') as json_file:
    json.dump(last_date, json_file, ensure_ascii=False, indent=4)

save_img(last_df, current_date_str)
