# 实验9：熟悉大数据可视化技术

## title

实验9：熟悉大数据可视化技术

## slug

exp-big-data-visualization-business-analysis

## interaction_mode

guided_template

## template_type

business_visualization_analysis

## description

读取企业经营业务明细数据，围绕不同图表任务选择合适字段组合，使用 Python 完成描述性分析、对比分析、结构分析和相关分析，理解业务问题、图表类型与字段选择之间的对应关系。

## allow_edit_generated_code

true

## instruction_content

```markdown
---

## 一、实验目标

通过本实验，你需要掌握：

- 使用 pandas 从数据库读取企业业务明细数据
- 理解数据可视化不是简单画图，而是围绕业务问题选择图表和字段
- 根据图表类型选择合适的数据字段组合
- 掌握描述性分析、对比分析、结构分析和相关分析图表的适用场景
- 使用 matplotlib 和 seaborn 绘制常见业务分析图表
- 观察图表标题、坐标轴、单位、排序、颜色和异常值说明对表达效果的影响
- 结合大数据与会计专业场景解释企业经营数据中的业务现象

---

## 二、实验任务

请完成以下任务：

1. 从数据库读取企业业务明细数据
2. 查看数据规模、字段结构和前几行数据
3. 计算销售收入、成本金额、毛利金额、毛利率、回款金额等关键指标
4. 为描述性分析选择合适图表与字段组合
5. 为对比分析选择合适图表与字段组合
6. 为结构分析选择合适图表与字段组合
7. 为相关分析选择合适图表与字段组合
8. 总结不同图表类型适合回答的业务问题

---

## 三、实验要求

- 必须正确连接数据库
- 必须成功读取 company_works_raw 企业业务数据表
- 必须能解释图表所回答的业务问题
- 必须区分描述性分析、对比分析、结构分析和相关分析
- 必须注意图表标题、坐标轴名称、单位、排序和颜色含义
- 必须结合财会业务语境解释图表，而不是只描述图形形状

---

## 四、数据说明

本实验默认源数据表为 company_works_raw，约 10000 行。

数据字段包括：

- 基础维度：记录编号、业务日期、区域、城市、事业部、销售渠道、客户类型、产品类别
- 经营指标：订单数量、销售收入、成本金额、毛利金额、毛利率、折扣率
- 财会指标：应收金额、回款金额、回款状态、发票状态
- 运营指标：库存周转天数、客户满意度、风险等级

---

## 五、图表选择提示

### 1. 描述性分析图表

用于回答“整体情况怎样”“趋势如何”“数据分布是否集中”等问题。

可选任务示例：

- 月度销售收入趋势折线图：日期字段 + 金额字段
- 销售收入分布直方图：连续金额字段
- 区域毛利率箱线图：类别字段 + 比例字段

### 2. 对比分析图表

用于回答“谁高谁低”“不同类别之间差异如何”等问题。

可选任务示例：

- 区域销售收入排名柱状图：区域字段 + 金额汇总字段
- 产品类别毛利率条形图：产品字段 + 比例均值字段
- 销售渠道收入回款分组柱状图：渠道字段 + 两个金额字段

### 3. 结构分析图表

用于回答“整体由哪些部分构成”“各部分占比是多少”等问题。

可选任务示例：

- 销售渠道收入占比饼图：渠道字段 + 金额字段
- 产品类别收入占比环形图：产品字段 + 金额字段
- 区域-产品类别收入堆叠柱状图：两个类别字段 + 金额字段

### 4. 相关分析图表

用于回答“两个指标之间是否存在关联”“指标变化方向是否一致”等问题。

可选任务示例：

- 折扣率与毛利率散点图：两个比例字段
- 销售收入与回款金额散点图：两个金额字段
- 财会经营指标相关系数热力图：多个数值字段

---

## 六、注意事项

- 本实验默认源数据库由教师统一提供
- 默认源数据表为 company_works_raw
- 参数区不是直接问“哪个字段是销售收入”，而是让你按图表任务选择字段组合
- 图表不是越复杂越好，关键是图表要服务业务问题
- 类别对比图建议先排序，再绘图
- 金额类指标要注意单位和小数位
- 毛利率、折扣率等比例指标要避免和金额指标混用同一坐标轴
- 图表结论需要结合业务背景，不应把相关关系直接解释为因果关系
```

## template_schema

```json
{
  "fields": [
    { "name": "db_name", "type": "text", "label": "个人数据库名", "default": "", "required": true, "placeholder": "例如：2025001001" },
    { "name": "db_user", "type": "text", "label": "数据库用户名", "default": "", "required": true, "placeholder": "例如：2025001001" },
    { "name": "db_password", "type": "password", "label": "数据库密码", "default": "", "required": true, "placeholder": "例如：s2025001001" },
    { "name": "raw_db_name", "type": "text", "label": "源数据库名", "default": "", "required": true, "placeholder": "例如：myclass2025" },
    { "name": "raw_tb_name", "type": "text", "label": "源数据表", "default": "company_works_raw", "required": true, "placeholder": "固定使用：company_works_raw" },
    { "max": 50, "min": 1, "name": "preview_count", "type": "number", "label": "展示前几条", "default": 10, "required": true, "placeholder": "例如：10" },
    { "max": 20, "min": 3, "name": "top_n", "type": "number", "label": "排名展示数量", "default": 8, "required": true, "placeholder": "例如：8" },
    {
      "name": "descriptive_chart",
      "type": "select",
      "label": "描述性分析：选择图表和字段组合",
      "default": "monthly_sales_line",
      "options": [
        { "label": "折线图：业务日期 + 销售收入，观察月度销售趋势", "value": "monthly_sales_line" },
        { "label": "直方图：销售收入，观察收入分布集中程度", "value": "sales_histogram" },
        { "label": "箱线图：区域 + 毛利率，观察区域毛利率差异和异常值", "value": "region_profit_box" }
      ],
      "required": true
    },
    {
      "name": "comparison_chart",
      "type": "select",
      "label": "对比分析：选择图表和字段组合",
      "default": "region_sales_bar",
      "options": [
        { "label": "柱状图：区域 + 销售收入，比较区域收入排名", "value": "region_sales_bar" },
        { "label": "条形图：产品类别 + 毛利率，比较产品盈利能力", "value": "product_profit_barh" },
        { "label": "复合图：销售渠道 + 销售收入/回款金额/回款率，比较渠道收入与回款效率", "value": "channel_collection_grouped" }
      ],
      "required": true
    },
    {
      "name": "structure_chart",
      "type": "select",
      "label": "结构分析：选择图表和字段组合",
      "default": "channel_sales_pie",
      "options": [
        { "label": "饼图：销售渠道 + 销售收入，观察渠道收入占比", "value": "channel_sales_pie" },
        { "label": "环形图：产品类别 + 销售收入，观察产品收入结构", "value": "product_sales_donut" },
        { "label": "堆叠柱状图：区域 + 产品类别 + 销售收入，观察区域产品结构", "value": "region_product_stacked" }
      ],
      "required": true
    },
    {
      "name": "correlation_chart",
      "type": "select",
      "label": "相关分析：选择图表和字段组合",
      "default": "discount_profit_scatter",
      "options": [
        { "label": "散点图：折扣率 + 毛利率，观察折扣对盈利能力的影响", "value": "discount_profit_scatter" },
        { "label": "散点图：销售收入 + 回款金额，观察收入与现金回收关系", "value": "sales_collection_scatter" },
        { "label": "热力图：多个财会经营指标，观察指标相关关系", "value": "finance_corr_heatmap" }
      ],
      "required": true
    }
  ]
}
```

## import_config

```json
{
  "fixed_imports": [
    "import json",
    "import pandas as pd",
    "import numpy as np",
    "import matplotlib.pyplot as plt",
    "import seaborn as sns",
    "from sqlalchemy import create_engine"
  ],
  "optional_imports": [],
  "allow_custom_import": false
}
```

## code_template

```python
# ========================
# 实验9：熟悉大数据可视化技术
# 主题：按业务问题选择图表和字段组合
# ========================

{{imports}}

# 第一步：连接个人数据库
engine = create_engine(
    f"mysql+pymysql://{{db_user}}:{{db_password}}@127.0.0.1:3306/{{db_name}}?charset=utf8mb4"
)

# 第二步：设置源库和源表
source_db = "{{raw_db_name}}"
source_table = "{{raw_tb_name}}"

if not source_db.replace("_", "").isalnum():
    raise ValueError("源数据库名只能包含字母、数字和下划线")

if not source_table.replace("_", "").isalnum():
    raise ValueError("源数据表名只能包含字母、数字和下划线")

# 第三步：读取企业业务数据
query = f"SELECT * FROM `{source_db}`.`{source_table}`"
df = pd.read_sql(query, engine)

# 第四步：查看前N条数据
preview_count = int({{preview_count}})
top_n = int({{top_n}})

print("【企业业务数据前几行】")
print(df.head(preview_count))

preview_rows = df.head(preview_count).to_dict(orient="records")
print("__TABLE_JSON__=" + json.dumps(preview_rows, ensure_ascii=False, default=str))

# 第五步：查看数据规模和字段
print()
print("【数据规模】")
print("数据行数：", len(df))
print("字段数量：", len(df.columns))
print("字段列表：", list(df.columns))

# 第六步：清洗字段并输出基础指标
required_cols = [
    "业务日期",
    "区域",
    "产品类别",
    "销售渠道",
    "销售收入",
    "成本金额",
    "毛利率",
    "折扣率",
    "回款金额",
]
missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
    raise ValueError("数据表中缺少字段：" + "、".join(missing_cols))

df["业务日期"] = pd.to_datetime(df["业务日期"], errors="coerce")
numeric_cols = ["销售收入", "成本金额", "毛利率", "折扣率", "回款金额"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=["业务日期"] + numeric_cols).copy()
df["月份"] = df["业务日期"].dt.to_period("M").astype(str)

summary_rows = pd.DataFrame([
    {"指标": "记录数量", "数值": int(len(df))},
    {"指标": "销售收入合计", "数值": round(float(df["销售收入"].sum()), 2)},
    {"指标": "成本金额合计", "数值": round(float(df["成本金额"].sum()), 2)},
    {"指标": "回款金额合计", "数值": round(float(df["回款金额"].sum()), 2)},
    {"指标": "平均毛利率", "数值": round(float(df["毛利率"].mean()), 4)},
    {"指标": "平均折扣率", "数值": round(float(df["折扣率"].mean()), 4)},
])

print()
print("【关键经营指标汇总】")
print(summary_rows)
print("__TABLE_JSON__=" + json.dumps(summary_rows.to_dict(orient="records"), ensure_ascii=False, default=str))

# ========================
# 当前从第七步开始带学生逐步取消注释
# 规则：代码行前使用一个井号，取消注释后即可运行
# 规则：说明性注释行前使用两个井号，取消注释后仍保留为注释
# ========================

## # 第七步：描述性分析图表
## # 目标：回答“整体趋势如何、数据分布怎样、是否存在异常值”
# sns.set_theme(style="whitegrid", font="SimHei")
# plt.rcParams["axes.unicode_minus"] = False
# descriptive_chart = "{{descriptive_chart}}"
#
# if descriptive_chart == "monthly_sales_line":
#     chart_data = df.groupby("月份", as_index=False)["销售收入"].sum()
#     print()
#     print("【描述性分析：月度销售收入趋势数据】")
#     print(chart_data)
#     print("__TABLE_JSON__=" + json.dumps(chart_data.to_dict(orient="records"), ensure_ascii=False, default=str))
#     plt.figure(figsize=(9, 4.8))
#     sns.lineplot(data=chart_data, x="月份", y="销售收入", marker="o", color="#2563eb")
#     plt.title("描述性分析：月度销售收入趋势")
#     plt.xlabel("月份")
#     plt.ylabel("销售收入")
#     plt.xticks(rotation=45)
#     plt.tight_layout()
#     plt.show()
#
# elif descriptive_chart == "sales_histogram":
#     describe_rows = df[["销售收入"]].describe().reset_index()
#     describe_rows.columns = ["统计项", "销售收入"]
#     print()
#     print("【描述性分析：销售收入分布统计】")
#     print(describe_rows)
#     print("__TABLE_JSON__=" + json.dumps(describe_rows.to_dict(orient="records"), ensure_ascii=False, default=str))
#     plt.figure(figsize=(8, 4.8))
#     sns.histplot(df["销售收入"], bins=30, kde=True, color="#60a5fa")
#     plt.title("描述性分析：销售收入分布")
#     plt.xlabel("销售收入")
#     plt.ylabel("记录数量")
#     plt.tight_layout()
#     plt.show()
#
# elif descriptive_chart == "region_profit_box":
#     chart_data = (
#         df.groupby("区域", as_index=False)
#         .agg(
#             平均毛利率=("毛利率", "mean"),
#             中位数毛利率=("毛利率", "median"),
#             最低毛利率=("毛利率", "min"),
#             最高毛利率=("毛利率", "max"),
#         )
#     )
#     print()
#     print("【描述性分析：区域毛利率分布统计】")
#     print(chart_data)
#     print("__TABLE_JSON__=" + json.dumps(chart_data.to_dict(orient="records"), ensure_ascii=False, default=str))
#     plt.figure(figsize=(8, 4.8))
#     sns.boxplot(data=df, x="区域", y="毛利率", color="#93c5fd")
#     plt.title("描述性分析：不同区域毛利率分布")
#     plt.xlabel("区域")
#     plt.ylabel("毛利率")
#     plt.tight_layout()
#     plt.show()

## # 第八步：对比分析图表
## # 目标：回答“哪些区域、产品或渠道表现更高或更低”
# comparison_chart = "{{comparison_chart}}"
#
# if comparison_chart == "region_sales_bar":
#     chart_data = df.groupby("区域", as_index=False)["销售收入"].sum().sort_values("销售收入", ascending=False).head(top_n)
#     print()
#     print("【对比分析：区域销售收入排名】")
#     print(chart_data)
#     print("__TABLE_JSON__=" + json.dumps(chart_data.to_dict(orient="records"), ensure_ascii=False, default=str))
#     plt.figure(figsize=(8, 4.8))
#     sns.barplot(data=chart_data, x="区域", y="销售收入", color="#3b82f6")
#     plt.title("对比分析：区域销售收入排名")
#     plt.xlabel("区域")
#     plt.ylabel("销售收入")
#     plt.tight_layout()
#     plt.show()
#
# elif comparison_chart == "product_profit_barh":
#     chart_data = df.groupby("产品类别", as_index=False)["毛利率"].mean().sort_values("毛利率", ascending=False)
#     print()
#     print("【对比分析：产品类别平均毛利率】")
#     print(chart_data)
#     print("__TABLE_JSON__=" + json.dumps(chart_data.to_dict(orient="records"), ensure_ascii=False, default=str))
#     plt.figure(figsize=(8, 4.8))
#     sns.barplot(data=chart_data, y="产品类别", x="毛利率", color="#22c55e")
#     plt.title("对比分析：产品类别平均毛利率")
#     plt.xlabel("平均毛利率")
#     plt.ylabel("产品类别")
#     plt.tight_layout()
#     plt.show()
#
# elif comparison_chart == "channel_collection_grouped":
#     chart_data = df.groupby("销售渠道", as_index=False)[["销售收入", "回款金额"]].sum().sort_values("销售收入", ascending=False)
#     chart_data["回款率"] = (chart_data["回款金额"] / chart_data["销售收入"]).round(4)
#     print()
#     print("【对比分析：销售渠道收入、回款金额与回款率】")
#     print(chart_data)
#     print("__TABLE_JSON__=" + json.dumps(chart_data.to_dict(orient="records"), ensure_ascii=False, default=str))
#     chart_long = chart_data.melt(id_vars="销售渠道", value_vars=["销售收入", "回款金额"], var_name="指标", value_name="金额")
#     fig, ax1 = plt.subplots(figsize=(9, 5))
#     sns.barplot(data=chart_long, x="销售渠道", y="金额", hue="指标", palette=["#22c55e", "#f59e0b"], ax=ax1)
#     ax1.set_title("对比分析：销售渠道收入、回款金额与回款率")
#     ax1.set_xlabel("销售渠道")
#     ax1.set_ylabel("金额")
#     ax1.grid(axis="y", linestyle="--", alpha=0.25)
#
#     ax2 = ax1.twinx()
#     x_positions = np.arange(len(chart_data))
#     ax2.plot(x_positions, chart_data["回款率"], color="#e11d48", marker="o", linewidth=2.8, markersize=7, label="回款率")
#     ax2.set_ylabel("回款率")
#     rate_min = max(0, chart_data["回款率"].min() - 0.05)
#     rate_max = min(1.05, chart_data["回款率"].max() + 0.05)
#     ax2.set_ylim(rate_min, rate_max)
#     rate_ticks = np.linspace(rate_min, rate_max, 5)
#     ax2.set_yticks(rate_ticks)
#     ax2.set_yticklabels([f"{tick:.0%}" for tick in rate_ticks])
#     for idx, rate in enumerate(chart_data["回款率"]):
#         ax2.text(idx, rate + 0.01, f"{rate:.1%}", ha="center", va="bottom", color="#e11d48", fontsize=9)
#
#     bar_handles, bar_labels = ax1.get_legend_handles_labels()
#     line_handles, line_labels = ax2.get_legend_handles_labels()
#     ax1.legend(bar_handles + line_handles, bar_labels + line_labels, loc="upper center", bbox_to_anchor=(0.5, 1.15), ncol=3, frameon=False)
#     plt.tight_layout()
#     plt.show()

## # 第九步：结构分析图表
## # 目标：回答“整体由哪些部分构成、各部分占比是多少”
# structure_chart = "{{structure_chart}}"
#
# if structure_chart == "channel_sales_pie":
#     chart_data = df.groupby("销售渠道", as_index=False)["销售收入"].sum().sort_values("销售收入", ascending=False)
#     chart_data["占比"] = (chart_data["销售收入"] / chart_data["销售收入"].sum()).round(4)
#     print()
#     print("【结构分析：销售渠道收入占比】")
#     print(chart_data)
#     print("__TABLE_JSON__=" + json.dumps(chart_data.to_dict(orient="records"), ensure_ascii=False, default=str))
#     plt.figure(figsize=(6.8, 6.8))
#     plt.pie(chart_data["销售收入"], labels=chart_data["销售渠道"], autopct="%1.1f%%", startangle=90, colors=sns.color_palette("pastel", len(chart_data)))
#     plt.title("结构分析：销售渠道收入占比")
#     plt.tight_layout()
#     plt.show()
#
# elif structure_chart == "product_sales_donut":
#     chart_data = df.groupby("产品类别", as_index=False)["销售收入"].sum().sort_values("销售收入", ascending=False)
#     chart_data["占比"] = (chart_data["销售收入"] / chart_data["销售收入"].sum()).round(4)
#     print()
#     print("【结构分析：产品类别收入占比】")
#     print(chart_data)
#     print("__TABLE_JSON__=" + json.dumps(chart_data.to_dict(orient="records"), ensure_ascii=False, default=str))
#     plt.figure(figsize=(6.8, 6.8))
#     plt.pie(chart_data["销售收入"], labels=chart_data["产品类别"], autopct="%1.1f%%", startangle=90, colors=sns.color_palette("pastel", len(chart_data)))
#     center_circle = plt.Circle((0, 0), 0.58, fc="white")
#     plt.gca().add_artist(center_circle)
#     plt.title("结构分析：产品类别收入占比")
#     plt.tight_layout()
#     plt.show()
#
# elif structure_chart == "region_product_stacked":
#     product_order = ["硬件设备", "软件订阅", "咨询服务", "财税服务", "维护服务"]
#     chart_data = pd.pivot_table(df, values="销售收入", index="区域", columns="产品类别", aggfunc="sum", fill_value=0)
#     chart_data = chart_data.reindex(columns=product_order, fill_value=0)
#     print()
#     print("【结构分析：区域-产品类别收入结构】")
#     print(chart_data)
#     print("__TABLE_JSON__=" + json.dumps(chart_data.reset_index().to_dict(orient="records"), ensure_ascii=False, default=str))
#     ax = chart_data.plot(kind="bar", stacked=True, figsize=(9, 5), colormap="tab20", edgecolor="white", width=0.75)
#     plt.title("结构分析：区域-产品类别收入结构")
#     plt.xlabel("区域")
#     plt.ylabel("销售收入")
#     plt.xticks(rotation=0)
#     plt.legend(title="产品类别", bbox_to_anchor=(1.02, 1), loc="upper left")
#     plt.grid(axis="y", linestyle="--", alpha=0.25)
#     plt.tight_layout()
#     plt.show()

## # 第十步：相关分析图表
## # 目标：回答“指标之间是否存在同向或反向关系”
# correlation_chart = "{{correlation_chart}}"
#
# if correlation_chart == "discount_profit_scatter":
#     chart_data = df[["折扣率", "毛利率", "区域"]].copy()
#     print()
#     print("【相关分析：折扣率与毛利率样本数据】")
#     print(chart_data.head(preview_count))
#     print("__TABLE_JSON__=" + json.dumps(chart_data.head(preview_count).to_dict(orient="records"), ensure_ascii=False, default=str))
#     plt.figure(figsize=(7.2, 5))
#     sns.scatterplot(data=chart_data, x="折扣率", y="毛利率", hue="区域", alpha=0.65, s=24)
#     plt.title("相关分析：折扣率与毛利率关系")
#     plt.xlabel("折扣率")
#     plt.ylabel("毛利率")
#     plt.legend(title="区域", bbox_to_anchor=(1.02, 1), loc="upper left")
#     plt.tight_layout()
#     plt.show()
#
# elif correlation_chart == "sales_collection_scatter":
#     chart_data = df[["销售收入", "回款金额", "销售渠道"]].copy()
#     print()
#     print("【相关分析：销售收入与回款金额样本数据】")
#     print(chart_data.head(preview_count))
#     print("__TABLE_JSON__=" + json.dumps(chart_data.head(preview_count).to_dict(orient="records"), ensure_ascii=False, default=str))
#     plt.figure(figsize=(7.2, 5))
#     sns.scatterplot(data=chart_data, x="销售收入", y="回款金额", hue="销售渠道", alpha=0.65, s=24)
#     plt.title("相关分析：销售收入与回款金额关系")
#     plt.xlabel("销售收入")
#     plt.ylabel("回款金额")
#     plt.legend(title="销售渠道", bbox_to_anchor=(1.02, 1), loc="upper left")
#     plt.tight_layout()
#     plt.show()
#
# elif correlation_chart == "finance_corr_heatmap":
#     corr_cols = ["订单数量", "销售收入", "成本金额", "毛利金额", "毛利率", "折扣率", "应收金额", "回款金额", "库存周转天数", "客户满意度"]
#     corr_cols = [col for col in corr_cols if col in df.columns]
#     corr_df = df[corr_cols].corr(numeric_only=True).round(4)
#     print()
#     print("【相关分析：财会经营指标相关系数】")
#     print(corr_df)
#     print("__TABLE_JSON__=" + json.dumps(corr_df.reset_index().to_dict(orient="records"), ensure_ascii=False, default=str))
#     plt.figure(figsize=(8, 6))
#     sns.heatmap(corr_df, annot=True, cmap="Blues", fmt=".2f", linewidths=0.5)
#     plt.title("相关分析：财会经营指标相关系数热力图")
#     plt.tight_layout()
#     plt.show()

## # 第十一步：图表选择总结
# chart_summary = pd.DataFrame([
#     {"分析类型": "描述性分析", "适合问题": "整体趋势、分布情况、异常值", "图表示例": "折线图、直方图、箱线图", "字段组合": "日期+金额、连续金额、类别+比例"},
#     {"分析类型": "对比分析", "适合问题": "不同类别谁高谁低", "图表示例": "柱状图、条形图、分组柱状图", "字段组合": "类别+汇总金额、类别+均值比例、类别+多个金额"},
#     {"分析类型": "结构分析", "适合问题": "整体由哪些部分构成", "图表示例": "饼图、环形图、堆叠柱状图", "字段组合": "类别+金额、两个类别+金额"},
#     {"分析类型": "相关分析", "适合问题": "指标之间是否存在关联", "图表示例": "散点图、相关系数热力图", "字段组合": "数值+数值、多个数值字段"},
# ])
#
# print()
# print("【图表选择总结】")
# print(chart_summary)
# print("__TABLE_JSON__=" + json.dumps(chart_summary.to_dict(orient="records"), ensure_ascii=False, default=str))
#
# print()
# print("【实验结论提示】")
# print("1. 先明确业务问题，再选择图表类型和字段组合。")
# print("2. 描述性分析适合看趋势、分布和异常值。")
# print("3. 对比分析适合比较类别差异，通常需要排序。")
# print("4. 结构分析适合解释整体构成和占比。")
# print("5. 相关分析可以发现指标关系，但相关不等于因果。")
```

## 数据准备 SQL

数据准备脚本见 [company_works_raw.sql](../table_raw/company_works_raw.sql)。
