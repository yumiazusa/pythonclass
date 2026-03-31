# Backend (FastAPI)

## 环境要求

- Python 3.11+
- MySQL 8.0+

## 安装依赖

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

guided_template（网页抓取实验）额外依赖已包含在 `requirements.txt`：

- `requests`
- `beautifulsoup4`
- `pandas`
- `numpy`
- `matplotlib`
- `seaborn`
- `scikit-learn`

## 配置环境变量

```bash
cp .env.example .env
```

`.env` 关键配置项：

- `MYSQL_HOST`、`MYSQL_PORT`、`MYSQL_USER`、`MYSQL_PASSWORD`、`MYSQL_DB`
- `JWT_SECRET_KEY`
- `JWT_ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `CODE_RUN_TIMEOUT_SECONDS`
- `CODE_RUN_MAX_OUTPUT_CHARS`
- `CODE_RUN_TEMP_DIR`

## 初始化数据库

先确保 MySQL 中已创建数据库：

```sql
CREATE DATABASE IF NOT EXISTS edu_code_platform DEFAULT CHARACTER SET utf8mb4;
```

再执行建表脚本：

```bash
python -m app.db.init_db
```

说明：`guided_template` 实验不会由初始化脚本自动写入具体模板内容，请在管理后台实验编辑页中配置 `template_schema / code_template / import_config`。

## 启动服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

推荐使用一键脚本（自动释放被占用端口后再启动）：

```bash
cd backend
./start_backend.sh
```

可选参数：

```bash
./start_backend.sh 8081
./start_backend.sh 8081 0.0.0.0 app.main:app
```

## 可用接口

- `GET /health`：健康检查接口
- `GET /api/users/test`：数据库连接测试接口
- `POST /api/auth/register`：注册接口
- `POST /api/auth/login`：登录接口
- `GET /api/auth/me`：获取当前登录用户
- `POST /api/auth/change-password`：当前用户修改密码
- `POST /api/auth/update-profile`：教师/管理员修改个人信息（用户名、姓名）
- `GET /api/docs`：文档列表（支持 `keyword`、`category`，仅返回已发布文档）
- `GET /api/docs/{slug}`：文档详情（仅已发布）
- `GET /api/docs/meta/categories`：文档分类列表（仅已发布）
- `GET /api/student/dashboard`：当前登录用户个人中心汇总（学生主页）
- `GET /api/admin/overview`：管理员后台首页概览（仅 admin）
- `GET /api/admin/docs`：管理员查询文档（支持 `keyword`、`category`）
- `GET /api/admin/docs/categories`：管理员查询所有文档分类
- `POST /api/admin/docs`：管理员新建文档
- `PUT /api/admin/docs/{doc_id}`：管理员更新文档
- `DELETE /api/admin/docs/{doc_id}`：管理员删除文档
- `GET /api/admin/experiments`：管理员分页查询实验（仅 admin）
- `POST /api/admin/experiments`：管理员创建实验（仅 admin）
- `GET /api/admin/experiments/{experiment_id}`：管理员获取实验详情（仅 admin）
- `PUT /api/admin/experiments/{experiment_id}`：管理员更新实验（仅 admin）
- `POST /api/admin/experiments/{experiment_id}/enable`：管理员启用实验（仅 admin）
- `POST /api/admin/experiments/{experiment_id}/disable`：管理员停用实验（仅 admin）
- `GET /api/admin/users`：管理员分页查询用户（仅 admin）
- `GET /api/admin/users/class-options`：管理员查询已存在班级选项（仅 admin）
- `GET /api/admin/admin-users`：管理员分页查询管理员账号（仅 admin）
- `POST /api/admin/admin-users`：管理员创建管理员账号（仅 admin）
- `POST /api/admin/admin-users/{user_id}/enable`：管理员启用管理员账号（仅 admin）
- `POST /api/admin/admin-users/{user_id}/disable`：管理员停用管理员账号（仅 admin）
- `POST /api/admin/admin-users/{user_id}/reset-password`：管理员重置管理员密码（仅 admin）
- `POST /api/admin/teachers`：管理员创建教师账号（仅 admin）
- `POST /api/admin/users/{user_id}/enable`：管理员启用用户（仅 admin）
- `POST /api/admin/users/{user_id}/disable`：管理员停用用户（仅 admin）
- `POST /api/admin/users/{user_id}/reset-password`：管理员重置用户密码（仅 admin）
- `POST /api/admin/users/{user_id}/set-role`：管理员设置已有账号角色（student/teacher/admin，仅 admin）
- `POST /api/admin/users/{user_id}/update-info`：管理员修改用户信息（用户名、姓名，仅 admin）
- `POST /api/admin/users/{user_id}/delete`：管理员删除单个用户账号（仅 admin）
- `POST /api/admin/users/batch-delete`：管理员批量删除用户账号（仅 admin）
- `POST /api/admin/users/batch-enable`：管理员批量启用用户账号（仅 admin）
- `POST /api/admin/users/batch-disable`：管理员批量停用用户账号（仅 admin）
- `POST /api/admin/users/batch-reset-password`：管理员批量重置用户密码（仅 admin）
- `POST /api/experiments`：创建实验（仅 teacher）
- `GET /api/experiments`：实验列表
- `GET /api/experiments/{experiment_id}`：实验详情
- `POST /api/experiments/guided-template/validate-imports`：校验 guided_template 自定义导入语句
- `POST /api/submissions/save`：保存草稿
- `POST /api/submissions/submit`：正式提交
- `GET /api/submissions/latest/{experiment_id}`：获取最新版本
- `GET /api/submissions/history/{experiment_id}`：获取历史版本列表
- `GET /api/submissions/{submission_id}`：获取提交详情
- `GET /api/submissions/workspace-status/{experiment_id}`：获取学生工作区状态
- `POST /api/code/run`：运行 Python 代码（需登录）
- `GET /api/teacher/experiments/overview`：教师实验概览统计（仅 teacher）
- `GET /api/teacher/experiments/{experiment_id}/export`：导出实验结果（仅 teacher）
- `GET /api/teacher/experiments/{experiment_id}/class-summary`：实验班级统计（仅 teacher）
- `GET /api/teacher/experiments/{experiment_id}/students`：教师查看实验学生最新状态（仅 teacher）
- `GET /api/teacher/experiments/{experiment_id}/students/{user_id}/history`：教师查看学生实验历史（仅 teacher）
- `GET /api/teacher/submissions/{submission_id}`：教师查看提交详情（仅 teacher）
- `POST /api/teacher/submissions/{submission_id}/review`：教师批阅提交（仅 teacher）
- `POST /api/teacher/experiments/{experiment_id}/students/{user_id}/return`：教师退回学生实验（仅 teacher）
- `POST /api/teacher/experiments/{experiment_id}/batch-return`：教师批量退回学生实验（仅 teacher）
- `GET /api/teacher/students`：教师分页查询学生账号（仅 teacher）
- `GET /api/teacher/students/export`：导出学生账号清单（仅 teacher）
- `POST /api/teacher/students/batch-reset-password`：批量重置学生密码（仅 teacher）
- `POST /api/teacher/students/{user_id}/enable`：启用学生账号（仅 teacher）
- `POST /api/teacher/students/{user_id}/disable`：停用学生账号（仅 teacher）
- `POST /api/teacher/students/batch-enable`：批量启用学生账号（仅 teacher）
- `POST /api/teacher/students/batch-disable`：批量停用学生账号（仅 teacher）
- `GET /api/teacher/students/import-template`：下载学生名单导入模板（仅 teacher）
- `POST /api/teacher/students/import`：教师上传 Excel 批量导入学生名单（仅 teacher）

## 提交批阅字段（code_submissions）

- `review_status`：批阅状态，`pending / passed / failed`
- `review_comment`：教师评语，可为空
- `reviewed_by`：批阅教师用户 ID，可为空
- `reviewed_at`：批阅时间，可为空

说明：

- 初始化脚本会在 `Base.metadata.create_all` 后补齐上述字段，兼容已有库表
- 新提交和退回后草稿会默认写入 `review_status = pending`
- 学生端 `latest/detail/history` 与教师端详情接口均会返回批阅字段

## 实验模式分层（第二十阶段）

- `experiments` 新增字段：
  - `interaction_mode`：实验交互模式，支持 `native_editor / guided_template`，默认 `native_editor`
  - `instruction_content`：实验说明正文（可用于替代简单 description）
  - `sort_order`：课程顺序字段，默认 `0`
- 第二十一阶段新增 guided_template 字段：
  - `template_type`：模板类型（例如 `web_scraping_table`）
  - `template_schema`：参数表单配置（JSON）
  - `code_template`：带占位符的代码模板
  - `import_config`：导入库配置（固定库/可选库/自定义导入）
  - `allow_edit_generated_code`：是否允许学生继续编辑生成代码
- 当前阶段行为：
  - `native_editor`：保持原有代码编辑器流程
  - `guided_template`：进入引导式参数页，支持“应用参数到代码 + 继续运行/保存/提交”
- 排序规则：
  - 学生实验列表默认按 `sort_order` 升序（再按实验 ID）
  - 管理员实验列表支持按 `sort_order` 等字段排序

### guided_template 导入库校验（第二十一阶段）

- 白名单至少包含：`requests / bs4 / pandas / numpy / matplotlib / seaborn / sklearn`
- 危险库黑名单：`os / sys / subprocess / socket / shutil / pathlib / ctypes / multiprocessing / threading`
- 支持语法：
  - `import xxx`
  - `from xxx import yyy`
- 前端可调用 `/api/experiments/guided-template/validate-imports` 做应用前校验
- 后端运行接口在 guided_template 模式下会做二次校验

## 学生名单 Excel 批量导入

- 模板下载接口：`GET /api/teacher/students/import-template`（后端动态生成模板，包含表头与示例行）
- 接口：`POST /api/teacher/students/import`
- 权限：仅教师
- 文件：仅支持 `.xlsx`
- 必要表头：`班级`、`学号`、`姓名`
- 可选表头：`序号`（会被忽略）
- 导入规则：
  - `username = 学号`
  - `student_no = 学号`
  - `class_name = 班级`
  - `full_name = 姓名`
  - `role = student`
  - 新建账号默认密码为 `123456`，入库前会做哈希
  - 新建账号默认 `must_change_password = true`（首次登录强制改密）
  - 若 `student_no` 已存在，默认更新 `class_name`、`full_name`，不修改密码与角色
- 逐行导入，单行错误不会导致整批失败，错误明细会在 `failed_items` 返回

## 学生账号管理（第十三阶段）

- 用户新增字段：`is_enabled`（默认 `true`）
- 用户新增字段：`must_change_password`（默认 `false`）
- 当 `is_enabled = false` 时，该账号登录会被拒绝（提示“该账号已被停用，请联系教师”）
- 教师可在学生管理接口中执行：
  - 批量重置密码（仅更新密码哈希，不返回真实密码；重置后将 `must_change_password = true`）
  - 启用/停用单个或多个学生账号
  - 导出账号清单（不包含真实密码和密码哈希）

## 管理后台第 1 步（管理员角色 + 后台首页）

- 角色扩展为：`student / teacher / admin`
- 管理员权限依赖：`CurrentAdmin`（仅 `role=admin` 可访问）
- 管理员首页接口：`GET /api/admin/overview`
  - 返回字段：
    - `total_users`
    - `student_count`
    - `teacher_count`
    - `admin_count`
    - `experiment_count`
    - `enabled_user_count`
    - `disabled_user_count`
    - `recent_created_users_count`（近 7 天）
    - `recent_submission_count`（近 7 天）

管理员测试账号设置（最小方式）：

```sql
UPDATE users SET role = 'admin' WHERE username = '你的用户名';
```

说明：

- 当前不提供公开“注册管理员”能力，`POST /api/auth/register` 会拒绝 `role=admin`
- 可通过数据库手动提升已有账号为 admin 进行测试

## 管理后台第 2 步（教师与用户管理）

- 用户总览：`GET /api/admin/users`
  - 支持筛选：`keyword`、`role`、`is_enabled`
  - 支持班级筛选：`class_name`
  - 支持分页：`page`、`page_size`（最大 100）
- 班级选项：`GET /api/admin/users/class-options`
  - 返回数据库中已存在的非空班级列表，可用于前端下拉筛选
- 创建教师：`POST /api/admin/teachers`
  - `role` 固定写入 `teacher`
  - 密码哈希后保存
  - 新教师默认 `must_change_password = true`
- 启用/停用用户：
  - `POST /api/admin/users/{user_id}/enable`
  - `POST /api/admin/users/{user_id}/disable`
  - 防止当前登录管理员停用自己
- 设置角色：`POST /api/admin/users/{user_id}/set-role`
  - 支持设置为 `student / teacher / admin`
  - 安全限制：不能把当前登录管理员改为非管理员角色
- 重置密码：`POST /api/admin/users/{user_id}/reset-password`
  - 新密码哈希保存
  - 重置后会写入 `must_change_password = true`
- 删除账号：
  - 单个删除：`POST /api/admin/users/{user_id}/delete`
  - 批量删除：`POST /api/admin/users/batch-delete`
  - 限制：当前登录管理员不能删除自己
  - 若删除目标为管理员账号，需额外满足：
    - 系统至少保留一个管理员账号
    - 系统至少保留一个启用中的管理员账号
- 批量账号维护：
  - 批量启用：`POST /api/admin/users/batch-enable`
  - 批量停用：`POST /api/admin/users/batch-disable`（会拒绝停用当前登录管理员自己）
  - 批量重置密码：`POST /api/admin/users/batch-reset-password`（会写入 `must_change_password = true`）
  - 说明：`/api/admin/users/*` 仅用于 student/teacher；管理员账号需走 `/api/admin/admin-users/*`

## 管理后台第 3 步（管理员账号创建与管理）

- 管理员列表：`GET /api/admin/admin-users`
  - 支持筛选：`keyword`、`is_enabled`
  - 支持分页：`page`、`page_size`（最大 100）
- 创建管理员：`POST /api/admin/admin-users`
  - `role` 固定为 `admin`
  - 新管理员默认 `is_enabled = true`
  - 新管理员默认 `must_change_password = true`
- 启用/停用管理员：
  - `POST /api/admin/admin-users/{user_id}/enable`
  - `POST /api/admin/admin-users/{user_id}/disable`
  - 安全限制：
    - 不能停用当前登录管理员自己
    - 系统必须至少保留一个启用中的管理员账号
- 重置管理员密码：`POST /api/admin/admin-users/{user_id}/reset-password`
  - 新密码哈希保存
  - 重置后会写入 `must_change_password = true`
- 删除管理员账号（通过通用删除接口）：`POST /api/admin/users/{user_id}/delete`
  - 不允许删除当前登录管理员自己
  - 仍需满足“至少保留一个管理员账号 + 至少保留一个启用中的管理员账号”

## 修改密码与首次登录强制改密（第十七阶段）

- 当前用户修改密码接口：`POST /api/auth/change-password`
- 登录用户信息（`/api/auth/me`）会返回 `must_change_password`
- 用户修改密码成功后会自动将 `must_change_password = false`

## 实验结果导出与班级统计（第十四阶段）

- 实验结果导出：`GET /api/teacher/experiments/{experiment_id}/export`
  - 支持沿用筛选参数：`keyword`、`class_name`、`student_no`、`status`、`review_status`、`sort_by`、`sort_order`
  - 导出字段仅包含教学管理相关数据，不包含密码或密码哈希
- 班级统计：`GET /api/teacher/experiments/{experiment_id}/class-summary`
  - 统计口径：按系统内学生账号（`role=student`）所属班级汇总该实验“最新提交状态 + 批阅状态”
  - `not_submitted_count = total_students - submitted_count`

## 学生个人中心（第十八阶段）

- 接口：`GET /api/student/dashboard`
- 权限：需登录；学生可访问，教师也可访问并查看自己的基础信息与实验摘要
- 统计口径（基于当前可见实验：已发布且启用）：
  - `submitted_count`：该实验最新记录状态为 `submitted`
  - `passed_count`：最新记录 `status=submitted` 且 `review_status=passed`
  - `failed_count`：最新记录 `status=submitted` 且 `review_status=failed`
  - `pending_count`：最新记录 `status=submitted` 且 `review_status=pending`（或空值）
  - `not_started_count`：该实验无任何提交记录
- `recent_items`：按当前用户各实验最新提交的更新时间倒序返回，默认最多 5 条

示例：

```bash
curl -X POST "http://127.0.0.1:8000/api/teacher/students/import" \
  -H "Authorization: Bearer <teacher_access_token>" \
  -F "file=@/path/to/students.xlsx"
```

## 认证接口示例

### 注册

```bash
curl -X POST "http://127.0.0.1:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student01",
    "password": "123456",
    "role": "student"
  }'
```

### 登录

```bash
curl -X POST "http://127.0.0.1:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student01",
    "password": "123456"
  }'
```

### 获取当前用户

```bash
curl -X GET "http://127.0.0.1:8000/api/auth/me" \
  -H "Authorization: Bearer <access_token>"
```

## 实验与代码记录接口示例

### 教师创建实验

```bash
curl -X POST "http://127.0.0.1:8000/api/experiments" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <teacher_access_token>" \
  -d '{
    "title": "实验1：Pandas数据读取",
    "slug": "exp-pandas-read",
    "description": "学习CSV读取与DataFrame基本查看",
    "starter_code": "import pandas as pd\n\nprint(\"hello\")",
    "is_active": true
  }'
```

### 查询实验列表

```bash
curl -X GET "http://127.0.0.1:8000/api/experiments" \
  -H "Authorization: Bearer <access_token>"
```

### 保存草稿

```bash
curl -X POST "http://127.0.0.1:8000/api/submissions/save" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "experiment_id": 1,
    "code": "import pandas as pd\nprint(\"draft\")",
    "run_output": "draft",
    "is_passed": true
  }'
```

### 正式提交

```bash
curl -X POST "http://127.0.0.1:8000/api/submissions/submit" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "experiment_id": 1,
    "code": "import pandas as pd\nprint(\"submitted\")",
    "run_output": "submitted",
    "is_passed": true
  }'
```

### 查询某实验最新版本

```bash
curl -X GET "http://127.0.0.1:8000/api/submissions/latest/1" \
  -H "Authorization: Bearer <access_token>"
```

### 查询某实验历史版本

```bash
curl -X GET "http://127.0.0.1:8000/api/submissions/history/1" \
  -H "Authorization: Bearer <access_token>"
```

## 代码运行接口示例

### 接口说明

- 路径：`POST /api/code/run`
- 权限：需登录（Bearer Token）
- 说明：当前为教学场景基础限制版，不是完整沙箱，生产环境建议升级为容器隔离

### 示例1：正常代码

```bash
curl -X POST "http://127.0.0.1:8000/api/code/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "code": "print(\"hello world\")"
  }'
```

### 示例2：报错代码

```bash
curl -X POST "http://127.0.0.1:8000/api/code/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "code": "print(1/0)"
  }'
```

### 示例3：危险代码

```bash
curl -X POST "http://127.0.0.1:8000/api/code/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "code": "import os\nprint(os.listdir())"
  }'
```

### 示例4：超时代码

```bash
curl -X POST "http://127.0.0.1:8000/api/code/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "code": "while True:\n    pass"
  }'
```
