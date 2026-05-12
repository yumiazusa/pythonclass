# 实验7：建立分类分析模型、执行分类分析

## 1. 实验定位

本实验面向大数据与会计专业学生，使用 `expense_account_raw` 企业费用报销审核数据表，完成一个财会业务分类任务。

分类目标：

根据报销记录中的部门、员工级别、费用类型、报销金额、发票金额、预算使用率、是否疑似重复发票等字段，预测该报销记录的 `审核结果`。

分类结果包括：

- `通过`
- `人工复核`
- `退回`

建议实验模式：

- `interaction_mode`：`guided_template`
- `template_type`：`knn_classification`
- `sort_order`：`70`
- 默认先设置为未发布，教师测试通过后再发布。

## 2. 学生操作流程

### 步骤1：连接数据库

学生在参数区填写 MySQL 地址、端口、用户名、密码、数据库名和表名。

默认表名：

```text
expense_account_raw
```

### 步骤2：读取并观察数据

运行后观察：

- 数据行数
- 数据列数
- 前几行数据
- `审核结果` 分类分布

系统会输出表格预览，并绘制 `审核结果` 类别分布柱状图。

### 步骤3：准备建模数据

处理规则：

- 删除 `记录编号`
- 将 `审核结果` 作为目标变量
- 其他字段作为特征变量
- 使用 `pd.get_dummies()` 将文字字段转换成数值字段

### 步骤4：划分训练集和测试集

建议默认：

```text
测试集比例 = 0.25
随机种子 = 42
```

### 步骤5：训练 K近邻分类模型

使用：

```python
KNeighborsClassifier
```

默认 K 值建议为：

```text
K = 5
```

### 步骤6：评价模型效果

输出：

- 测试集准确率
- 分类报告
- 混淆矩阵热力图
- 不同 K 值的准确率变化曲线

## 3. template_schema

```json
{
  "fields": [
    {
      "name": "db_host",
      "label": "步骤1：数据库地址",
      "type": "text",
      "required": true,
      "default": "127.0.0.1",
      "placeholder": "例如：127.0.0.1"
    },
    {
      "name": "db_port",
      "label": "步骤1：数据库端口",
      "type": "number",
      "required": true,
      "min": 1,
      "max": 65535,
      "step": 1,
      "default": 3306,
      "placeholder": "例如：3306"
    },
    {
      "name": "db_user",
      "label": "步骤1：数据库用户名",
      "type": "text",
      "required": true,
      "default": "edu_user",
      "placeholder": "例如：edu_user 或 root"
    },
    {
      "name": "db_password",
      "label": "步骤1：数据库密码",
      "type": "password",
      "required": true,
      "default": "edu_password",
      "placeholder": "请输入 MySQL 密码"
    },
    {
      "name": "db_name",
      "label": "步骤1：数据库名",
      "type": "text",
      "required": true,
      "default": "edu_code_platform",
      "placeholder": "例如：edu_code_platform"
    },
    {
      "name": "table_name",
      "label": "步骤1：数据表名",
      "type": "text",
      "required": true,
      "default": "expense_account_raw",
      "placeholder": "固定使用：expense_account_raw"
    },
    {
      "name": "preview_count",
      "label": "步骤2：预览数据行数",
      "type": "number",
      "required": true,
      "min": 5,
      "max": 30,
      "step": 1,
      "default": 10,
      "placeholder": "建议：10"
    },
    {
      "name": "test_size",
      "label": "步骤4：测试集比例",
      "type": "number",
      "required": true,
      "min": 0.1,
      "max": 0.5,
      "step": 0.05,
      "default": 0.25,
      "placeholder": "建议：0.25"
    },
    {
      "name": "k_neighbors",
      "label": "步骤5：K近邻的K值",
      "type": "number",
      "required": true,
      "min": 1,
      "max": 25,
      "step": 2,
      "default": 5,
      "placeholder": "建议选择奇数，如 5 或 7"
    },
    {
      "name": "max_k",
      "label": "步骤6：K值对比最大值",
      "type": "number",
      "required": true,
      "min": 5,
      "max": 31,
      "step": 2,
      "default": 21,
      "placeholder": "用于绘制K值准确率曲线"
    },
    {
      "name": "random_state",
      "label": "步骤4：随机种子",
      "type": "number",
      "required": true,
      "min": 0,
      "max": 9999,
      "step": 1,
      "default": 42,
      "placeholder": "建议：42"
    }
  ]
}
```

## 4. import_config

```json
{
  "fixed_imports": [
    "import json",
    "import pymysql",
    "import pandas as pd",
    "import numpy as np",
    "import matplotlib.pyplot as plt",
    "import seaborn as sns",
    "from sklearn.model_selection import train_test_split",
    "from sklearn.preprocessing import StandardScaler",
    "from sklearn.neighbors import KNeighborsClassifier",
    "from sklearn.metrics import accuracy_score, classification_report, confusion_matrix"
  ],
  "optional_imports": [],
  "allow_custom_import": false
}
```

## 5. code_template

```python
{{imports}}

# 实验7：K近邻分类分析
# 数据表：expense_account_raw
# 目标字段：审核结果

DB_HOST = "{{db_host}}"
DB_PORT = {{db_port}}
DB_USER = "{{db_user}}"
DB_PASSWORD = "{{db_password}}"
DB_NAME = "{{db_name}}"
TABLE_NAME = "{{table_name}}"
PREVIEW_COUNT = int({{preview_count}})
TEST_SIZE = float({{test_size}})
K_NEIGHBORS = int({{k_neighbors}})
MAX_K = int({{max_k}})
RANDOM_STATE = int({{random_state}})

if not TABLE_NAME.replace("_", "").isalnum():
    raise ValueError("数据表名只能包含字母、数字和下划线")

connection = pymysql.connect(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    charset="utf8mb4"
)

try:
    sql = f"SELECT * FROM `{TABLE_NAME}`"
    df = pd.read_sql(sql, connection)
finally:
    connection.close()

print("一、读取数据")
print("数据表：", TABLE_NAME)
print("数据规模：", df.shape[0], "行，", df.shape[1], "列")
print("字段列表：", list(df.columns))
print()

preview_rows = df.head(PREVIEW_COUNT).to_dict(orient="records")
print("__TABLE_JSON__=" + json.dumps(preview_rows, ensure_ascii=False))

print("二、审核结果分布")
label_counts = df["审核结果"].value_counts()
print(label_counts)
print()

plt.figure(figsize=(7, 4))
label_counts.plot(kind="bar", color=["#60a5fa", "#34d399", "#f87171"])
plt.title("审核结果类别分布")
plt.xlabel("审核结果")
plt.ylabel("记录数量")
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()

print("三、准备建模数据")
target_col = "审核结果"
drop_cols = ["记录编号"]
feature_df = df.drop(columns=drop_cols + [target_col])
y = df[target_col]

X = pd.get_dummies(feature_df, drop_first=False)
print("原始特征列数：", feature_df.shape[1])
print("编码后特征列数：", X.shape[1])
print()

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=TEST_SIZE,
    random_state=RANDOM_STATE,
    stratify=y
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("四、划分数据集")
print("训练集：", X_train.shape[0], "行")
print("测试集：", X_test.shape[0], "行")
print("测试集比例：", TEST_SIZE)
print()

model = KNeighborsClassifier(n_neighbors=K_NEIGHBORS)
model.fit(X_train_scaled, y_train)
y_pred = model.predict(X_test_scaled)
accuracy = accuracy_score(y_test, y_pred)

print("五、K近邻模型结果")
print("K值：", K_NEIGHBORS)
print("测试集准确率：{:.4f}".format(accuracy))
print()
print("分类报告：")
print(classification_report(y_test, y_pred, zero_division=0))

k_values = list(range(1, MAX_K + 1, 2))
accuracy_values = []
for k in k_values:
    temp_model = KNeighborsClassifier(n_neighbors=k)
    temp_model.fit(X_train_scaled, y_train)
    temp_pred = temp_model.predict(X_test_scaled)
    accuracy_values.append(accuracy_score(y_test, temp_pred))

best_index = int(np.argmax(accuracy_values))
print("六、不同K值对比")
print("本次对比K值：", k_values)
print("最高准确率K值：", k_values[best_index])
print("最高准确率：{:.4f}".format(accuracy_values[best_index]))
print()

plt.figure(figsize=(7, 4))
plt.plot(k_values, accuracy_values, marker="o", color="#2563eb")
plt.title("不同K值的测试集准确率")
plt.xlabel("K值")
plt.ylabel("准确率")
plt.xticks(k_values)
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

labels = sorted(y.unique())
cm = confusion_matrix(y_test, y_pred, labels=labels)

plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=labels, yticklabels=labels)
plt.title("K近邻分类混淆矩阵")
plt.xlabel("模型预测结果")
plt.ylabel("真实审核结果")
plt.tight_layout()
plt.show()

print("七、实验结论提示")
print("1. 准确率越高，说明整体分类效果越好，但不能只看准确率。")
print("2. 请结合分类报告观察每一类的 precision、recall 和 f1-score。")
print("3. 请结合混淆矩阵观察哪些审核结果容易被混淆。")
print("4. 尝试修改K值，再运行一次，比较图中的准确率变化。")
```

## 6. 思考题

1. K 值从 1 增大到 21 时，准确率有什么变化？
2. 哪个审核结果最容易被模型判断错？
3. 为什么 K近邻算法需要先做标准化？
4. 在真实财会审核中，模型预测为 `退回` 是否可以直接替代人工判断？

