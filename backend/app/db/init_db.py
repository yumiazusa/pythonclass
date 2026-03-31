import argparse

import pymysql
from sqlalchemy import select

from app.core.config import get_settings
from app.db.base_class import Base
from app.db.session import SessionLocal, engine
from app.models import code_submission, doc, experiment, user
from app.models.code_submission import CodeSubmission
from app.models.doc import Doc
from app.models.experiment import Experiment
from app.models.user import User


def init_db() -> None:
    ensure_database_exists()
    Base.metadata.create_all(bind=engine)
    ensure_experiment_schedule_columns()
    ensure_user_profile_columns()
    ensure_user_enabled_column()
    ensure_user_must_change_password_column()
    ensure_submission_review_columns()
    ensure_default_docs()


def _build_default_docs() -> list[dict]:
    return [
        {
            "title": "Python基础",
            "slug": "python-basic",
            "category": "基础入门",
            "sort_order": 10,
            "summary": "变量、类型、条件循环与函数入门。",
            "content": (
                "# Python基础\n\n"
                "## 1. 变量与类型\n\n"
                "- `int` 整数\n"
                "- `float` 小数\n"
                "- `str` 字符串\n"
                "- `list` 列表\n"
                "- `dict` 字典\n\n"
                "```python\n"
                "name = \"Alice\"\n"
                "score = 95\n"
                "passed = score >= 60\n"
                "print(name, score, passed)\n"
                "```\n\n"
                "## 2. 条件与循环\n\n"
                "```python\n"
                "for i in range(1, 6):\n"
                "    if i % 2 == 0:\n"
                "        print(i, \"是偶数\")\n"
                "```\n\n"
                "## 3. 函数\n\n"
                "```python\n"
                "def add(a, b):\n"
                "    return a + b\n\n"
                "print(add(3, 5))\n"
                "```\n"
            ),
            "is_published": True,
        },
        {
            "title": "Pandas基础",
            "slug": "pandas-basic",
            "category": "基础入门",
            "sort_order": 20,
            "summary": "DataFrame 读取、过滤、分组与缺失值处理。",
            "content": (
                "# Pandas基础\n\n"
                "Pandas 主要用于表格数据分析，核心对象是 `DataFrame`。\n\n"
                "```python\n"
                "import pandas as pd\n\n"
                "df = pd.read_csv(\"students.csv\")\n"
                "print(df.head())\n"
                "print(df.info())\n"
                "```\n\n"
                "- 选择列：`df[[\"姓名\", \"成绩\"]]`\n"
                "- 条件过滤：`df[df[\"成绩\"] >= 60]`\n"
                "- 分组统计：`df.groupby(\"班级\")[\"成绩\"].mean()`\n"
            ),
            "is_published": True,
        },
        {
            "title": "数据清洗",
            "slug": "data-cleaning",
            "category": "数据处理",
            "sort_order": 30,
            "summary": "缺失值、重复值、异常值处理与清洗流程。",
            "content": (
                "# 数据清洗\n\n"
                "常见问题：缺失值、重复数据、异常值、格式不统一。\n\n"
                "1. 查看数据概况\n"
                "2. 统一字段格式\n"
                "3. 处理缺失与异常\n"
                "4. 去重并验证结果\n\n"
                "```python\n"
                "df = df.drop_duplicates()\n"
                "df[\"age\"] = df[\"age\"].fillna(df[\"age\"].median())\n"
                "```\n"
            ),
            "is_published": True,
        },
        {
            "title": "线性回归",
            "slug": "linear-regression",
            "category": "机器学习",
            "sort_order": 40,
            "summary": "预测连续值的基础模型与常见评估指标。",
            "content": (
                "# 线性回归\n\n"
                "`y = w1*x1 + w2*x2 + ... + b`\n\n"
                "```python\n"
                "from sklearn.linear_model import LinearRegression\n\n"
                "model = LinearRegression()\n"
                "model.fit(X_train, y_train)\n"
                "pred = model.predict(X_test)\n"
                "```\n\n"
                "常见评估：MAE / MSE / R²。\n"
            ),
            "is_published": True,
        },
        {
            "title": "分类",
            "slug": "classification",
            "category": "机器学习",
            "sort_order": 50,
            "summary": "离散标签预测任务与常见评价指标。",
            "content": (
                "# 分类\n\n"
                "```python\n"
                "from sklearn.linear_model import LogisticRegression\n\n"
                "clf = LogisticRegression(max_iter=1000)\n"
                "clf.fit(X_train, y_train)\n"
                "print(clf.score(X_test, y_test))\n"
                "```\n\n"
                "常见指标：Accuracy、Precision、Recall、F1-score。\n"
            ),
            "is_published": True,
        },
        {
            "title": "聚类",
            "slug": "clustering",
            "category": "机器学习",
            "sort_order": 60,
            "summary": "无监督分组任务，K-Means 入门。",
            "content": (
                "# 聚类\n\n"
                "```python\n"
                "from sklearn.cluster import KMeans\n\n"
                "kmeans = KMeans(n_clusters=3, random_state=42)\n"
                "labels = kmeans.fit_predict(X)\n"
                "```\n\n"
                "说明：建议先做特征缩放，并尝试不同 `n_clusters`。\n"
            ),
            "is_published": True,
        },
        {
            "title": "图表基础",
            "slug": "charts-basic",
            "category": "可视化",
            "sort_order": 70,
            "summary": "折线图、柱状图、散点图的基本使用。",
            "content": (
                "# 图表基础\n\n"
                "- 折线图：趋势变化\n"
                "- 柱状图：类别对比\n"
                "- 散点图：相关关系\n\n"
                "```python\n"
                "import matplotlib.pyplot as plt\n\n"
                "plt.plot([1, 2, 3], [2, 4, 3])\n"
                "plt.title(\"趋势图\")\n"
                "plt.show()\n"
                "```\n"
            ),
            "is_published": True,
        },
        {
            "title": "如何完成实验",
            "slug": "how-to-finish-lab",
            "category": "实验指南",
            "sort_order": 80,
            "summary": "实验学习与提交流程建议。",
            "content": (
                "# 如何完成实验\n\n"
                "1. 在实验列表选择实验\n"
                "2. 阅读实验说明与目标\n"
                "3. 在编辑器完成代码\n"
                "4. 先运行，再保存草稿\n"
                "5. 自检通过后提交\n\n"
                "```python\n"
                "print(df.head())\n"
                "print(df.shape)\n"
                "```\n"
            ),
            "is_published": True,
        },
        {
            "title": "管理员实验新建操作说明（原生模式 / 引导式模板模式）",
            "slug": "admin-experiment-create-guide",
            "category": "管理员手册",
            "sort_order": 90,
            "summary": "管理员创建 native_editor 与 guided_template 实验的操作说明与配置示例。",
            "content": (
                "# 管理员实验新建操作说明\n\n"
                "> 适用角色：`admin`\n"
                "> 可见范围：建议保持“未发布”，仅在管理员文档管理中查看。\n\n"
                "## 一、入口位置\n\n"
                "1. 登录管理员账号\n"
                "2. 进入 `后台实验管理`\n"
                "3. 点击 `新建实验`\n\n"
                "## 二、原生模式（native_editor）实验新建\n\n"
                "### 1. 基础字段\n\n"
                "- 实验模式：`native_editor`\n"
                "- 标题：例如 `实验1：Python基础语法`\n"
                "- slug：例如 `exp-python-basic`（必须唯一）\n"
                "- 启用状态：建议 `启用`\n"
                "- 发布状态：调试期间可先 `未发布`\n\n"
                "### 2. 关键内容\n\n"
                "- `starter_code`：学生进入编辑器看到的初始代码\n"
                "- `instruction_content`：实验说明正文（支持 Markdown）\n"
                "- `open_at / due_at`：按教学安排配置开放/截止时间\n\n"
                "### 3. 最佳实践\n\n"
                "- `starter_code` 放最小可运行示例，不要放完整答案\n"
                "- 截止时间应晚于开放时间\n"
                "- 首次发布前先用“进入测试”验证\n\n"
                "## 三、引导式模板模式（guided_template）实验新建\n\n"
                "### 1. 基础字段\n\n"
                "- 实验模式：`guided_template`\n"
                "- template_type：可按业务命名，如 `web_scraping_table`\n"
                "- allow_edit_generated_code：建议 `true`（学生可继续编辑）\n\n"
                "### 2. 必填配置（数据库驱动）\n\n"
                "必须配置以下 3 个字段：\n\n"
                "- `template_schema`（JSON）\n"
                "- `import_config`（JSON）\n"
                "- `code_template`（文本）\n\n"
                "如果缺少这些字段，学生进入页面会提示“模板尚未配置完整”。\n\n"
                "### 3. template_schema 示例\n\n"
                "```json\n"
                "{\n"
                "  \"fields\": [\n"
                "    {\n"
                "      \"name\": \"target_url\",\n"
                "      \"label\": \"目标网址\",\n"
                "      \"type\": \"text\",\n"
                "      \"required\": true,\n"
                "      \"default\": \"\",\n"
                "      \"placeholder\": \"例如：https://example.com\"\n"
                "    },\n"
                "    {\n"
                "      \"name\": \"user_agent\",\n"
                "      \"label\": \"请求头模板\",\n"
                "      \"type\": \"select\",\n"
                "      \"required\": true,\n"
                "      \"default\": \"\",\n"
                "      \"placeholder\": \"请选择请求头模板\",\n"
                "      \"options\": [\n"
                "        {\n"
                "          \"value\": \"ua_1\",\n"
                "          \"label\": \"Chrome 请求头\",\n"
                "          \"headers\": {\n"
                "            \"User-Agent\": \"Mozilla/5.0 ...\",\n"
                "            \"Accept\": \"text/html,...\"\n"
                "          }\n"
                "        }\n"
                "      ]\n"
                "    },\n"
                "    {\n"
                "      \"name\": \"preview_count\",\n"
                "      \"label\": \"展示前几条\",\n"
                "      \"type\": \"number\",\n"
                "      \"required\": true,\n"
                "      \"min\": 1,\n"
                "      \"max\": 100,\n"
                "      \"default\": null,\n"
                "      \"placeholder\": \"例如：10\"\n"
                "    }\n"
                "  ]\n"
                "}\n"
                "```\n\n"
                "### 4. import_config 示例\n\n"
                "```json\n"
                "{\n"
                "  \"fixed_imports\": [],\n"
                "  \"optional_imports\": [\"requests\", \"bs4\", \"pandas\"],\n"
                "  \"allow_custom_import\": true\n"
                "}\n"
                "```\n\n"
                "### 5. code_template 示例\n\n"
                "```python\n"
                "{{imports}}\n\n"
                "url = \"{{target_url}}\"\n"
                "headers = {{headers_block}}\n\n"
                "print(\"preview:\", {{preview_count}})\n"
                "```\n\n"
                "说明：占位符由学生点击“应用参数到代码”后替换。\n\n"
                "### 6. DataFrame 卡片显示（推荐写法）\n\n"
                "如果希望运行结果在前端 `表格数据（DataFrame）` 卡片中展示，而不是只显示在 stdout 里，\n"
                "请在代码末尾增加“标记输出”：\n\n"
                "```python\n"
                "import json\n\n"
                "preview_count = int({{preview_count}})\n"
                "table_rows = df.head(preview_count).to_dict(orient=\"records\")\n\n"
                "# 关键：使用 __TABLE_JSON__ 标记，前端会识别为表格数据\n"
                "print(\"__TABLE_JSON__=\" + json.dumps(table_rows, ensure_ascii=False))\n"
                "```\n\n"
                "建议：\n\n"
                "- 保留上述标记输出用于表格卡片渲染\n"
                "- 避免再次 `print(json.dumps(table_rows, ...))`（无标记版本），以免 stdout 出现长 JSON\n"
                "- 可减少 `print(df.head(...))` 等大段文本输出，提升结果页可读性\n\n"
                "## 四、发布前检查清单\n\n"
                "- [ ] 标题、slug 已确认且唯一\n"
                "- [ ] 实验模式选择正确\n"
                "- [ ] open_at / due_at 时间合理\n"
                "- [ ] guided_template 三大字段已完整配置\n"
                "- [ ] 管理员“进入测试”验证通过\n"
                "- [ ] 再切换为“已发布”\n\n"
                "## 五、常见问题\n\n"
                "1. 学生提示“模板未配置完整”\n"
                "   原因：`template_schema / code_template / import_config` 缺失或结构错误。\n\n"
                "2. 学生无法进入实验\n"
                "   检查：是否已发布、是否到开放时间、是否已截止。\n\n"
                "3. slug 重复报错\n"
                "   处理：修改为唯一 slug（建议带课程/章节标识）。\n"
            ),
            "is_published": False,
        },
    ]


def ensure_default_docs() -> None:
    db = SessionLocal()
    try:
        for item in _build_default_docs():
            existed = db.execute(select(Doc).where(Doc.slug == item["slug"])).scalar_one_or_none()
            if existed:
                if item["slug"] == "admin-experiment-create-guide":
                    existed.title = item["title"]
                    existed.content = item["content"]
                    existed.summary = item.get("summary")
                    existed.category = item.get("category") or "未分类"
                    existed.sort_order = int(item.get("sort_order") or 0)
                continue
            db.add(
                Doc(
                    title=item["title"],
                    slug=item["slug"],
                    content=item["content"],
                    summary=item.get("summary"),
                    category=item.get("category") or "未分类",
                    sort_order=int(item.get("sort_order") or 0),
                    is_published=bool(item.get("is_published", True)),
                )
            )
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def ensure_database_exists() -> None:
    settings = get_settings()
    db_name = settings.mysql_db.replace("`", "")
    connection = pymysql.connect(
        host=settings.mysql_host,
        port=settings.mysql_port,
        user=settings.mysql_user,
        password=settings.mysql_password,
        charset="utf8mb4",
        autocommit=True,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` DEFAULT CHARACTER SET utf8mb4")
    finally:
        connection.close()


def ensure_submission_review_columns() -> None:
    settings = get_settings()
    db_name = settings.mysql_db.replace("`", "")
    connection = pymysql.connect(
        host=settings.mysql_host,
        port=settings.mysql_port,
        user=settings.mysql_user,
        password=settings.mysql_password,
        database=db_name,
        charset="utf8mb4",
        autocommit=True,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute("SHOW COLUMNS FROM `code_submissions` LIKE 'review_status'")
            has_review_status = bool(cursor.fetchone())
            if not has_review_status:
                cursor.execute(
                    "ALTER TABLE `code_submissions` ADD COLUMN `review_status` VARCHAR(20) NOT NULL DEFAULT 'pending'"
                )
                has_review_status = True
            cursor.execute("SHOW COLUMNS FROM `code_submissions` LIKE 'review_comment'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE `code_submissions` ADD COLUMN `review_comment` TEXT NULL")
            cursor.execute("SHOW COLUMNS FROM `code_submissions` LIKE 'reviewed_by'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE `code_submissions` ADD COLUMN `reviewed_by` INT NULL")
            cursor.execute("SHOW COLUMNS FROM `code_submissions` LIKE 'reviewed_at'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE `code_submissions` ADD COLUMN `reviewed_at` DATETIME NULL")

            cursor.execute("SHOW INDEX FROM `code_submissions` WHERE Key_name = 'ix_code_submissions_review_status'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE `code_submissions` ADD INDEX `ix_code_submissions_review_status` (`review_status`)")
            cursor.execute("SHOW INDEX FROM `code_submissions` WHERE Key_name = 'ix_code_submissions_reviewed_by'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE `code_submissions` ADD INDEX `ix_code_submissions_reviewed_by` (`reviewed_by`)")

            cursor.execute(
                """
                SELECT CONSTRAINT_NAME
                FROM information_schema.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = %s
                  AND TABLE_NAME = 'code_submissions'
                  AND COLUMN_NAME = 'reviewed_by'
                  AND REFERENCED_TABLE_NAME = 'users'
                """,
                (db_name,),
            )
            if not cursor.fetchone():
                cursor.execute(
                    """
                    ALTER TABLE `code_submissions`
                    ADD CONSTRAINT `fk_code_submissions_reviewed_by_users`
                    FOREIGN KEY (`reviewed_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
                    """
                )
            if has_review_status:
                cursor.execute("UPDATE `code_submissions` SET `review_status` = 'pending' WHERE `review_status` IS NULL")
    finally:
        connection.close()


def ensure_experiment_schedule_columns() -> None:
    settings = get_settings()
    db_name = settings.mysql_db.replace("`", "")
    connection = pymysql.connect(
        host=settings.mysql_host,
        port=settings.mysql_port,
        user=settings.mysql_user,
        password=settings.mysql_password,
        database=db_name,
        charset="utf8mb4",
        autocommit=True,
    )
    try:
        with connection.cursor() as cursor:
            is_published_added = False
            cursor.execute("SHOW COLUMNS FROM `experiments` LIKE 'is_published'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE `experiments` ADD COLUMN `is_published` TINYINT(1) NOT NULL DEFAULT 0")
                is_published_added = True
            cursor.execute("SHOW COLUMNS FROM `experiments` LIKE 'instruction_content'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE `experiments` ADD COLUMN `instruction_content` TEXT NULL")
            cursor.execute("SHOW COLUMNS FROM `experiments` LIKE 'interaction_mode'")
            if not cursor.fetchone():
                cursor.execute(
                    "ALTER TABLE `experiments` ADD COLUMN `interaction_mode` VARCHAR(32) NOT NULL DEFAULT 'native_editor'"
                )
            cursor.execute("SHOW COLUMNS FROM `experiments` LIKE 'sort_order'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE `experiments` ADD COLUMN `sort_order` INT NOT NULL DEFAULT 0")
            cursor.execute("SHOW COLUMNS FROM `experiments` LIKE 'template_type'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE `experiments` ADD COLUMN `template_type` VARCHAR(64) NULL")
            cursor.execute("SHOW COLUMNS FROM `experiments` LIKE 'template_schema'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE `experiments` ADD COLUMN `template_schema` JSON NULL")
            cursor.execute("SHOW COLUMNS FROM `experiments` LIKE 'code_template'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE `experiments` ADD COLUMN `code_template` LONGTEXT NULL")
            cursor.execute("SHOW COLUMNS FROM `experiments` LIKE 'import_config'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE `experiments` ADD COLUMN `import_config` JSON NULL")
            cursor.execute("SHOW COLUMNS FROM `experiments` LIKE 'allow_edit_generated_code'")
            if not cursor.fetchone():
                cursor.execute(
                    "ALTER TABLE `experiments` ADD COLUMN `allow_edit_generated_code` TINYINT(1) NOT NULL DEFAULT 1"
                )
            cursor.execute("SHOW COLUMNS FROM `experiments` LIKE 'open_at'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE `experiments` ADD COLUMN `open_at` DATETIME NULL")
            cursor.execute("SHOW COLUMNS FROM `experiments` LIKE 'due_at'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE `experiments` ADD COLUMN `due_at` DATETIME NULL")
            cursor.execute("SHOW INDEX FROM `experiments` WHERE Key_name = 'ix_experiments_interaction_mode'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE `experiments` ADD INDEX `ix_experiments_interaction_mode` (`interaction_mode`)")
            cursor.execute("SHOW INDEX FROM `experiments` WHERE Key_name = 'ix_experiments_sort_order'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE `experiments` ADD INDEX `ix_experiments_sort_order` (`sort_order`)")
            cursor.execute("SHOW INDEX FROM `experiments` WHERE Key_name = 'ix_experiments_template_type'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE `experiments` ADD INDEX `ix_experiments_template_type` (`template_type`)")
            cursor.execute("SHOW INDEX FROM `experiments` WHERE Key_name = 'ix_experiments_is_published'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE `experiments` ADD INDEX `ix_experiments_is_published` (`is_published`)")
            cursor.execute("SHOW INDEX FROM `experiments` WHERE Key_name = 'ix_experiments_open_at'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE `experiments` ADD INDEX `ix_experiments_open_at` (`open_at`)")
            cursor.execute("SHOW INDEX FROM `experiments` WHERE Key_name = 'ix_experiments_due_at'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE `experiments` ADD INDEX `ix_experiments_due_at` (`due_at`)")
            cursor.execute(
                "UPDATE `experiments` SET `interaction_mode` = 'native_editor' "
                "WHERE `interaction_mode` IS NULL OR `interaction_mode` = ''"
            )
            cursor.execute("UPDATE `experiments` SET `sort_order` = 0 WHERE `sort_order` IS NULL")
            cursor.execute(
                "UPDATE `experiments` SET `allow_edit_generated_code` = 1 "
                "WHERE `allow_edit_generated_code` IS NULL"
            )
            if is_published_added:
                cursor.execute("UPDATE `experiments` SET `is_published` = 1 WHERE `is_active` = 1")
    finally:
        connection.close()


def ensure_user_profile_columns() -> None:
    settings = get_settings()
    db_name = settings.mysql_db.replace("`", "")
    connection = pymysql.connect(
        host=settings.mysql_host,
        port=settings.mysql_port,
        user=settings.mysql_user,
        password=settings.mysql_password,
        database=db_name,
        charset="utf8mb4",
        autocommit=True,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute("SHOW COLUMNS FROM `users` LIKE 'student_no'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE `users` ADD COLUMN `student_no` VARCHAR(32) NULL")
            cursor.execute("SHOW COLUMNS FROM `users` LIKE 'class_name'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE `users` ADD COLUMN `class_name` VARCHAR(64) NULL")
            cursor.execute("SHOW COLUMNS FROM `users` LIKE 'full_name'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE `users` ADD COLUMN `full_name` VARCHAR(64) NULL")
            cursor.execute("SHOW INDEX FROM `users` WHERE Key_name = 'ix_users_student_no'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE `users` ADD INDEX `ix_users_student_no` (`student_no`)")
            cursor.execute("SHOW INDEX FROM `users` WHERE Key_name = 'ix_users_class_name'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE `users` ADD INDEX `ix_users_class_name` (`class_name`)")
    finally:
        connection.close()


def ensure_user_enabled_column() -> None:
    settings = get_settings()
    db_name = settings.mysql_db.replace("`", "")
    connection = pymysql.connect(
        host=settings.mysql_host,
        port=settings.mysql_port,
        user=settings.mysql_user,
        password=settings.mysql_password,
        database=db_name,
        charset="utf8mb4",
        autocommit=True,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute("SHOW COLUMNS FROM `users` LIKE 'is_enabled'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE `users` ADD COLUMN `is_enabled` TINYINT(1) NOT NULL DEFAULT 1")
            cursor.execute("SHOW INDEX FROM `users` WHERE Key_name = 'ix_users_is_enabled'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE `users` ADD INDEX `ix_users_is_enabled` (`is_enabled`)")
            cursor.execute("UPDATE `users` SET `is_enabled` = 1 WHERE `is_enabled` IS NULL")
    finally:
        connection.close()


def ensure_user_must_change_password_column() -> None:
    settings = get_settings()
    db_name = settings.mysql_db.replace("`", "")
    connection = pymysql.connect(
        host=settings.mysql_host,
        port=settings.mysql_port,
        user=settings.mysql_user,
        password=settings.mysql_password,
        database=db_name,
        charset="utf8mb4",
        autocommit=True,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute("SHOW COLUMNS FROM `users` LIKE 'must_change_password'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE `users` ADD COLUMN `must_change_password` TINYINT(1) NOT NULL DEFAULT 0")
            cursor.execute("SHOW INDEX FROM `users` WHERE Key_name = 'ix_users_must_change_password'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE `users` ADD INDEX `ix_users_must_change_password` (`must_change_password`)")
            cursor.execute("UPDATE `users` SET `must_change_password` = 0 WHERE `must_change_password` IS NULL")
    finally:
        connection.close()


def _get_or_create_teacher(db):
    from app.core.security import get_password_hash

    teacher = db.execute(select(User).where(User.username == "teacher_demo")).scalar_one_or_none()
    if teacher:
        return teacher
    teacher = User(
        username="teacher_demo",
        password_hash=get_password_hash("123456"),
        role="teacher",
    )
    db.add(teacher)
    db.flush()
    return teacher


def _get_or_create_experiment(db, title: str, slug: str, starter_code: str):
    exp = db.execute(select(Experiment).where(Experiment.slug == slug)).scalar_one_or_none()
    if exp:
        return exp
    exp = Experiment(
        title=title,
        slug=slug,
        description=f"{title} 测试实验",
        instruction_content=f"{title} 测试实验说明",
        starter_code=starter_code,
        interaction_mode="native_editor",
        sort_order=0,
        is_active=True,
        is_published=True,
        open_at=None,
        due_at=None,
    )
    db.add(exp)
    db.flush()
    return exp


def _build_student_profile(index: int) -> tuple[str, str]:
    class_names = ["高一(1)班", "高一(2)班", "高一(3)班", "高一(4)班", "高二(1)班", "高二(2)班"]
    class_name = class_names[(index - 1) % len(class_names)]
    student_no = f"2026{index:04d}"
    return student_no, class_name


def _get_or_create_student(db, username: str, student_no: str, class_name: str, full_name: str):
    from app.core.security import get_password_hash

    student = db.execute(select(User).where(User.username == username)).scalar_one_or_none()
    if student:
        student.student_no = student_no
        student.class_name = class_name
        student.full_name = full_name
        db.add(student)
        return student
    student = User(
        username=username,
        password_hash=get_password_hash("123456"),
        role="student",
        student_no=student_no,
        class_name=class_name,
        full_name=full_name,
    )
    db.add(student)
    db.flush()
    return student


def _seed_submissions(db, student_id: int, experiment_id: int, status_plan: list[str]):
    exists = db.execute(
        select(CodeSubmission.id).where(
            CodeSubmission.user_id == student_id,
            CodeSubmission.experiment_id == experiment_id,
        )
    ).first()
    if exists:
        return

    for index, status in enumerate(status_plan, start=1):
        base = index * (student_id + experiment_id)
        run_output = f"case-{student_id}-{experiment_id}-v{index}: {base}"
        submission = CodeSubmission(
            user_id=student_id,
            experiment_id=experiment_id,
            code=f"print({base})",
            status=status,
            run_output=run_output,
            is_passed=(status == "submitted"),
            review_status="pending",
            review_comment=None,
            reviewed_by=None,
            reviewed_at=None,
            version=index,
        )
        db.add(submission)


def _plan_for_experiment_a(idx: int) -> list[str]:
    if idx % 3 == 0:
        return ["draft", "submitted"]
    if idx % 3 == 1:
        return ["draft", "draft", "submitted"]
    return ["draft", "draft"]


def _plan_for_experiment_b(idx: int) -> list[str]:
    if idx % 4 == 0:
        return ["draft", "submitted"]
    if idx % 4 == 1:
        return ["draft"]
    if idx % 4 == 2:
        return ["draft", "draft", "submitted"]
    return ["draft", "draft"]


def _plan_for_experiment_c(idx: int) -> list[str]:
    if idx % 5 == 0:
        return ["draft", "draft", "submitted"]
    if idx % 2 == 0:
        return ["draft", "submitted"]
    return ["draft"]


def _backfill_all_student_profiles(db, force_reset: bool = False) -> int:
    students = db.execute(select(User).where(User.role == "student").order_by(User.id.asc())).scalars().all()
    updated_count = 0
    for index, student in enumerate(students, start=1):
        target_student_no, target_class_name = _build_student_profile(index)
        changed = False
        if force_reset or (not student.student_no):
            student.student_no = target_student_no
            changed = True
        if force_reset or (not student.class_name):
            student.class_name = target_class_name
            changed = True
        if force_reset or (not student.full_name):
            student.full_name = student.username
            changed = True
        if changed:
            db.add(student)
            updated_count += 1
    return updated_count


def seed_demo_data(student_count: int = 30, include_large_scene: bool = False) -> None:
    db = SessionLocal()
    try:
        _get_or_create_teacher(db)
        experiment_a = _get_or_create_experiment(
            db,
            title="实验A：循环与分支",
            slug="exp-a-loop-branch",
            starter_code='print("hello")',
        )
        experiment_b = _get_or_create_experiment(
            db,
            title="实验B：函数与列表",
            slug="exp-b-func-list",
            starter_code="def solve():\n    return []",
        )
        experiment_c = _get_or_create_experiment(
            db,
            title="实验C：字符串与字典",
            slug="exp-c-str-dict",
            starter_code="def normalize(text):\n    return text.strip()",
        )

        width = max(2, len(str(student_count)))
        student_names = [f"student{i:0{width}d}" for i in range(1, student_count + 1)]
        students = []
        for idx, name in enumerate(student_names, start=1):
            student_no, class_name = _build_student_profile(idx)
            students.append(
                _get_or_create_student(
                    db,
                    username=name,
                    student_no=student_no,
                    class_name=class_name,
                    full_name=name,
                )
            )

        for idx, student in enumerate(students, start=1):
            _seed_submissions(db, student.id, experiment_a.id, _plan_for_experiment_a(idx))
            _seed_submissions(db, student.id, experiment_b.id, _plan_for_experiment_b(idx))
            if include_large_scene:
                _seed_submissions(db, student.id, experiment_c.id, _plan_for_experiment_c(idx))

        _backfill_all_student_profiles(db)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def backfill_student_profiles() -> None:
    db = SessionLocal()
    try:
        _backfill_all_student_profiles(db)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def reset_student_profiles() -> None:
    db = SessionLocal()
    try:
        _backfill_all_student_profiles(db, force_reset=True)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed-demo", action="store_true")
    parser.add_argument("--demo-students", type=int, default=30)
    parser.add_argument("--seed-demo-large", action="store_true")
    parser.add_argument("--backfill-student-profiles", action="store_true")
    parser.add_argument("--force-reset-student-profiles", action="store_true")
    args = parser.parse_args()
    should_init = args.seed_demo or (
        not args.seed_demo and not args.backfill_student_profiles and not args.force_reset_student_profiles
    )
    if should_init:
        init_db()
    if args.seed_demo:
        count = max(args.demo_students, 1)
        seed_demo_data(student_count=count, include_large_scene=args.seed_demo_large or count >= 80)
    if args.backfill_student_profiles:
        backfill_student_profiles()
    if args.force_reset_student_profiles:
        reset_student_profiles()
