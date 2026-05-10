# PROJECT_CONTEXT.md

本文档是 PythonClass 项目的唯一长期主上下文文件。后续 Codex、ChatGPT、新设备或新协作者接手项目时，应优先阅读本文档，再阅读 `README.md`、`backend/README.md`、`frontend/README.md` 和具体代码。

本文档合并两类上下文：

- 工程平台版：工程结构、页面结构、API 契约、用户体系、前后端目录、数据模型、管理后台、教师端、学生端、UI 约束。
- 教学实验版：guided_template 架构、教学实验体系、数据分析课程设计、Python 沙盒、MySQL 教学体系、财务专业学生定位、分步教学业务逻辑。

## 目录结构

1. 项目定位
2. 用户体系与核心场景
3. 技术栈与工程结构
4. 页面结构
5. API 契约摘要
6. 数据模型摘要
7. 学生端、教师端与管理后台
8. UI 与产品设计约束
9. 教学实验体系
10. guided_template 核心系统
11. Python 沙盒机制
12. 数据库教学体系
13. 长期开发原则
14. 后续维护建议
15. 文档更新规范
16. 内容来源说明

## 1. 项目定位

PythonClass 是用于《大数据分析技术与基础》课程的在线 Python 数据分析实验平台。

项目真实定位非常重要：

- 本项目不是 Online Judge。
- 本项目不是以算法刷题、判题排名、AC 结果为中心的竞赛系统。
- 本项目是面向财务专业学生的数据分析教学平台。
- 本项目的目标不是培养程序员，而是帮助学生理解数据分析流程、掌握基础 Python 工具、完成课程实验，并能解释数据结果背后的业务意义。

平台应优先服务课堂内外的实验练习、代码运行、实验提交、结果查看和教师批阅。

## 2. 用户体系与核心场景

### 用户角色

- 学生：最高优先级用户，核心任务是进入实验、理解任务、完成代码、运行、保存和提交。
- 教师：负责实验发布、学生账号管理、实验结果查看、提交批阅、退回与导出。
- 管理员：负责平台级用户、教师、管理员账号、文档、实验和基础数据管理。

### 学生核心路径

学生主路径必须清晰稳定：

1. 登录。
2. 查看个人中心或实验列表。
3. 进入实验。
4. 阅读实验说明。
5. 通过 native_editor 或 guided_template 完成代码。
6. 运行代码并查看反馈。
7. 保存草稿。
8. 正式提交。
9. 查看批阅状态、教师评语和历史版本。

### 教师核心路径

教师侧重点是课堂管理效率：

1. 创建或维护实验。
2. 查看实验统计。
3. 查看学生最新提交状态。
4. 查看学生历史记录。
5. 批阅、退回或批量退回。
6. 导入学生名单。
7. 启用、停用、重置学生账号。
8. 导出实验结果或学生账号清单。

### 管理员核心路径

管理员侧重点是平台治理：

1. 查看后台概览。
2. 管理学生、教师、管理员账号。
3. 管理文档。
4. 管理实验。
5. 启用、停用、重置、删除、批量操作用户。

## 3. 技术栈与工程结构

### 技术栈

- 后端：FastAPI、SQLAlchemy、MySQL、Python 3.11+。
- 前端：Vue 3、Vite、Vue Router、Axios、Monaco Editor、Markdown 渲染、代码高亮。
- 数据库：MySQL 8.0+。
- Python 实验依赖：`requests`、`beautifulsoup4`、`pandas`、`numpy`、`matplotlib`、`seaborn`、`scikit-learn` 等。

### 仓库结构

```text
pythonclass/
├── backend/                # FastAPI 后端
├── frontend/               # Vue 3 + Vite 前端
├── docs/                   # 项目文档
├── AGENTS.md               # 设计协作约束
├── PROJECT_CONTEXT.md      # 长期主上下文
├── README.md               # 快速启动说明
└── .gitignore
```

### 后端分层

- `backend/app/api`：路由层与 API 聚合。
- `backend/app/api/v1/endpoints`：各业务模块接口。
- `backend/app/crud`：数据库读写层。
- `backend/app/models`：SQLAlchemy ORM 模型。
- `backend/app/schemas`：请求与响应模型。
- `backend/app/services`：业务服务，例如代码运行、导出、guided_template、学生导入。
- `backend/app/db`：数据库连接、初始化和兼容字段补齐。
- `backend/app/core`：配置、安全与认证。

### 前端分层

- `frontend/src/api`：接口封装。
- `frontend/src/views`：页面视图。
- `frontend/src/components`：通用组件。
- `frontend/src/router`：路由。
- `frontend/src/utils`：工具函数。
- `frontend/src/assets`：全局样式与资源。

## 4. 页面结构

### 公共页面

- 首页。
- 登录页。
- 修改密码页。
- 个人资料页。
- 文档页。

### 学生页面

- 学生仪表盘。
- 实验列表。
- native_editor 代码编辑页。
- guided_template 引导式实验页。
- 提交结果、历史版本和批阅反馈相关页面或区域。

### 教师页面

- 教师实验概览。
- 教师实验详情。
- 学生提交详情。
- 学生管理页。
- 学生导入页。

### 管理员页面

- 管理员后台概览。
- 用户管理。
- 教师管理。
- 管理员账号管理。
- 实验管理。
- 实验表单。
- 文档管理。

## 5. API 契约摘要

### 基础与认证

- `GET /health`：健康检查。
- `GET /api/users/test`：数据库连接测试。
- `POST /api/auth/register`：注册。
- `POST /api/auth/login`：登录。
- `GET /api/auth/me`：获取当前登录用户。
- `POST /api/auth/change-password`：当前用户修改密码。
- `POST /api/auth/update-profile`：教师或管理员修改个人信息。

### 文档

- `GET /api/docs`：文档列表。
- `GET /api/docs/{slug}`：文档详情。
- `GET /api/docs/meta/categories`：文档分类。
- `GET /api/admin/docs`：管理员查询文档。
- `POST /api/admin/docs`：管理员新建文档。
- `PUT /api/admin/docs/{doc_id}`：管理员更新文档。
- `DELETE /api/admin/docs/{doc_id}`：管理员删除文档。

### 实验

- `GET /api/experiments`：实验列表。
- `GET /api/experiments/{experiment_id}`：实验详情。
- `POST /api/experiments`：教师创建实验。
- `POST /api/experiments/guided-template/validate-imports`：校验 guided_template 自定义导入语句。
- `GET /api/admin/experiments`：管理员分页查询实验。
- `POST /api/admin/experiments`：管理员创建实验。
- `GET /api/admin/experiments/{experiment_id}`：管理员获取实验详情。
- `PUT /api/admin/experiments/{experiment_id}`：管理员更新实验。
- `POST /api/admin/experiments/{experiment_id}/enable`：管理员启用实验。
- `POST /api/admin/experiments/{experiment_id}/disable`：管理员停用实验。

### 提交与代码运行

- `POST /api/code/run`：运行 Python 代码，需登录。
- `POST /api/submissions/save`：保存草稿。
- `POST /api/submissions/submit`：正式提交。
- `GET /api/submissions/latest/{experiment_id}`：获取最新版本。
- `GET /api/submissions/history/{experiment_id}`：获取历史版本列表。
- `GET /api/submissions/{submission_id}`：获取提交详情。
- `GET /api/submissions/workspace-status/{experiment_id}`：获取学生工作区状态。

### 教师

- `GET /api/teacher/experiments/overview`：教师实验概览统计。
- `GET /api/teacher/experiments/{experiment_id}/export`：导出实验结果。
- `GET /api/teacher/experiments/{experiment_id}/class-summary`：实验班级统计。
- `GET /api/teacher/experiments/{experiment_id}/students`：查看实验学生最新状态。
- `GET /api/teacher/experiments/{experiment_id}/students/{user_id}/history`：查看学生实验历史。
- `GET /api/teacher/submissions/{submission_id}`：查看提交详情。
- `POST /api/teacher/submissions/{submission_id}/review`：批阅提交。
- `POST /api/teacher/experiments/{experiment_id}/students/{user_id}/return`：退回学生实验。
- `POST /api/teacher/experiments/{experiment_id}/batch-return`：批量退回。
- `GET /api/teacher/students`：分页查询学生账号。
- `GET /api/teacher/students/export`：导出学生账号清单。
- `GET /api/teacher/students/import-template`：下载学生名单导入模板。
- `POST /api/teacher/students/import`：上传 Excel 批量导入学生名单。

### 管理员

- `GET /api/admin/overview`：后台首页概览。
- `GET /api/admin/users`：分页查询用户。
- `GET /api/admin/users/class-options`：查询班级选项。
- `POST /api/admin/teachers`：创建教师账号。
- `GET /api/admin/admin-users`：分页查询管理员账号。
- `POST /api/admin/admin-users`：创建管理员账号。
- `POST /api/admin/users/{user_id}/enable`：启用用户。
- `POST /api/admin/users/{user_id}/disable`：停用用户。
- `POST /api/admin/users/{user_id}/reset-password`：重置密码。
- `POST /api/admin/users/{user_id}/set-role`：设置角色。
- `POST /api/admin/users/{user_id}/update-info`：修改用户信息。
- `POST /api/admin/users/{user_id}/delete`：删除单个用户。
- `POST /api/admin/users/batch-delete`：批量删除。
- `POST /api/admin/users/batch-enable`：批量启用。
- `POST /api/admin/users/batch-disable`：批量停用。
- `POST /api/admin/users/batch-reset-password`：批量重置密码。

## 6. 数据模型摘要

### users

用户表承担学生、教师、管理员三类角色。

关键字段包括：

- `username`：用户名。学生场景通常等于学号。
- `hashed_password`：密码哈希。
- `role`：`student / teacher / admin`。
- `student_no`：学号。
- `class_name`：班级。
- `full_name`：姓名。
- `is_enabled`：账号是否启用。
- `must_change_password`：是否强制首次改密。

### experiments

实验表承担课程实验配置与展示。

关键字段包括：

- `title`：实验标题。
- `description`：简要描述。
- `instruction_content`：实验说明正文。
- `sort_order`：课程排序。
- `interaction_mode`：`native_editor / guided_template`。
- `template_type`：模板类型。
- `template_schema`：参数表单配置，JSON。
- `code_template`：带占位符的代码模板。
- `import_config`：导入库配置。
- `allow_edit_generated_code`：是否允许学生继续编辑生成代码。

### code_submissions

提交表承担草稿、正式提交、历史版本与批阅结果。

关键字段包括：

- `review_status`：`pending / passed / failed`。
- `review_comment`：教师评语。
- `reviewed_by`：批阅教师 ID。
- `reviewed_at`：批阅时间。

### docs

文档表承担课程文档、平台说明、实验资料等内容管理。

## 7. 学生端、教师端与管理后台

### 学生端

学生端必须优先保证实验路径短、反馈明确、状态可恢复。保存草稿、运行结果、提交状态、历史版本和教师评语都应可见。

### 教师端

教师端应优先保证班级管理和批阅效率。学生导入支持 `.xlsx`，必要表头为 `班级`、`学号`、`姓名`，可选表头 `序号` 会被忽略。新建学生默认密码为 `123456`，并要求首次登录改密。

### 管理后台

管理员端负责平台治理。管理员角色只能由已有账号通过数据库或受控后台流程提升，不提供公开注册管理员能力。

## 8. UI 与产品设计约束

### 设计上下文

- 用户优先级：学生优先。
- 使用场景：课堂内外实验练习、代码运行、提交与结果查看。
- 品牌关键词：有活力、清晰、鼓励成长。
- 情绪目标：让用户感到可进步、可掌控、可持续学习。
- 语气：友好但专业，减少压迫感与复杂度。

### 视觉方向

- 极简教学风。
- 仅浅色模式。
- 淡蓝色为主色基调。
- 中性灰用于信息层级。
- 参考高质量排版与卡片组织方式，但不做花哨堆砌。

### 设计原则

1. 学习优先：登录、选实验、编码、运行、提交必须清晰可见。
2. 极简不单调：通过淡蓝层级、留白和精细间距体现活力。
3. 强反馈：保存、运行、提交、批阅必须有明确状态与结果反馈。
4. 信息分层：主任务高对比，次要信息弱化。
5. 一致性：学生端、教师端、管理员端共享统一控件语言与交互节奏。
6. 视觉基线冻结：后续迭代以增量优化为主，不随意改动稳定颜色、排版与组件形态。
7. 质量目标：优先保证可读性、可触达性与跨端一致体验。

## 9. 教学实验体系

### 9.1 项目真实定位

本项目不是 Online Judge。本项目是面向财务专业学生的数据分析教学平台。

教学目标不是让学生自由刷题或追求复杂编程技巧，而是让学生在低门槛、强引导的环境中理解数据采集、数据存储、数据清洗、建模分析、结果解释和业务表达。

### 9.2 教学设计原则

- 分步教学：实验内容按课堂节奏逐步展开。
- 逐步取消注释：初始代码保留必要注释和占位，课堂中逐步开放。
- 参数化实验：学生通过参数选择和表单配置理解关键变量。
- 低代码引导：降低语法负担，突出数据分析任务。
- 面向非计算机专业学生：默认学生编程基础有限。
- 强调数据分析理解：重点是数据来源、字段含义、清洗逻辑、模型输入输出。
- 强调业务解释能力：要求学生能解释分析结果在财务或业务场景中的意义。

### 9.3 实验体系

- 实验1：Python 基础数据类型。帮助学生理解字符串、数字、列表、字典、表格数据等基础概念，为后续数据分析打底。
- 实验2：网页数据抓取。通过 guided_template 引导学生配置 URL、请求头、User-Agent、解析规则和目标字段，理解网页数据采集流程。
- 实验3：MySQL 读表与字段设计。引导学生理解数据库、数据表、字段类型、主键、字段含义和从 MySQL 读取分析数据的过程。
- 实验4：数据清洗。围绕缺失值、重复值、异常值、字段类型转换、格式规范化等任务，建立分析前处理意识。
- 实验5：回归分析。引导学生理解自变量、因变量、训练数据、拟合结果、评价指标和财务业务解释。
- 实验6：关联规则分析。引导学生理解项集、支持度、置信度、提升度，以及关联规则在业务分析中的解释方式。

### 9.4 实验设计原则

所有实验都应遵循课堂逐步展开原则：

1. 初始版本先注释关键代码和关键概念。
2. 课堂中逐步取消注释。
3. 根据教学进度逐步放开代码。
4. 不一次性开放完整代码。
5. 不把实验设计成纯自由编程任务。
6. 每个实验都应保留明确的教学目标、操作步骤、运行反馈和结果解释要求。

## 10. guided_template 核心系统

guided_template 不是辅助功能，而是本项目最核心的教学系统。

### 核心定位

- guided_template 是将教学实验从“自由写代码”转为“参数化、可引导、可配置”的关键机制。
- guided_template 应服务财务专业学生，降低编程门槛，强化数据分析思维。
- guided_template 应让学生先理解任务、参数、字段和结果，再逐步接触完整代码。

### 当前能力

- 实验可通过 `interaction_mode` 区分 `native_editor` 与 `guided_template`。
- guided_template 可配置 `template_type`、`template_schema`、`code_template`、`import_config`。
- 学生在引导式参数页应用参数生成代码，并继续运行、保存和提交。
- 导入库需要前端校验和后端二次校验。

### 数据驱动原则

guided_template 必须数据库驱动：

- 实验模板不允许写死在前端代码里。
- 实验模板不允许写死在后端业务逻辑里。
- 参数配置必须可后台管理。
- 请求头模板必须可配置。
- User-Agent 模板必须可配置。
- 字段类型选项必须可配置。
- guided_template 参数必须来自数据库配置。
- 后续新增实验优先通过数据库配置扩展，而不是通过硬编码扩展。

### 导入库校验

- 白名单至少包括：`requests`、`bs4`、`pandas`、`numpy`、`matplotlib`、`seaborn`、`sklearn`。
- 危险库黑名单包括：`os`、`sys`、`subprocess`、`socket`、`shutil`、`pathlib`、`ctypes`、`multiprocessing`、`threading`。
- 支持语法：`import xxx`、`from xxx import yyy`。
- 前端调用 `/api/experiments/guided-template/validate-imports` 做应用前校验。
- 后端运行接口在 guided_template 模式下必须做二次校验。

## 11. Python 沙盒机制

当前系统采用统一 Python 沙盒运行，而不是每学生独立 Notebook Kernel。

原因：

- 服务器资源有限。
- 独立 Notebook Kernel 对内存、进程和生命周期管理要求更高。
- 当前课程目标更适合短时运行、结果反馈和提交保存。
- 统一沙盒更容易控制超时、输出长度、危险导入和运行目录。

当前沙盒相关配置应通过环境变量控制：

- `CODE_RUN_TIMEOUT_SECONDS`。
- `CODE_RUN_MAX_OUTPUT_CHARS`。
- `CODE_RUN_TEMP_DIR`。

后续若引入更强隔离机制，应优先保证教学体验、服务器可承受和安全边界清晰。

## 12. 数据库教学体系

数据库不仅是平台存储层，也是课程教学内容的一部分。

### 教学数据库原则

- 支持每学生独立数据库。
- 支持公共课程数据库。
- 支持 MySQL 数据分析实验。
- 可使用学号作为学生数据库名。
- 数据库实验应帮助学生理解表、字段、字段类型、查询、读表和数据分析之间的关系。

### 数据来源设计

- 公共课程数据库用于统一样例、课堂演示和共享数据。
- 学生独立数据库用于个人实验、提交和个性化练习。
- 实验数据配置应尽量可后台管理，避免把教学数据路径和字段规则写死在代码中。

## 13. 长期开发原则

1. 优先增量修改。
2. 不随意重构。
3. 不修改无关功能。
4. 修改前先列出文件。
5. guided_template 必须保持稳定。
6. 所有实验优先数据库驱动。
7. 面向财务专业学生。
8. 教学优先于自由编程。

补充原则：

- 新功能优先复用现有样式系统、接口分层和数据模型。
- 涉及学生主路径的改动必须格外谨慎。
- 涉及代码运行、提交、批阅、权限、数据库初始化的改动必须验证基本流程。
- 不为了技术洁癖进行大范围重构。
- 每次修改都应说明影响范围、验证方式和后续风险。

## 14. 后续维护建议

- 将本文档作为长期主上下文，避免多个上下文文件互相冲突。
- `README.md` 负责快速启动，本文档负责项目定位、设计决策、长期原则和业务上下文。
- `backend/README.md` 负责后端接口和启动细节，本文档只保留摘要和稳定原则。
- `frontend/README.md` 负责前端启动和构建细节，本文档只保留架构和设计约束。
- 新增实验时，先补充教学目标、参数配置、模板字段、预期反馈，再开发功能。
- 新增 guided_template 类型时，优先考虑是否能通过 `template_schema`、`code_template` 和 `import_config` 配置完成。
- 涉及数据库教学体系的变更，应同步记录学生独立数据库、公共课程数据库和字段设计规则。

## 15. 文档更新规范

更新本文档时遵循以下规则：

1. 只记录长期有效的上下文，不记录临时调试过程。
2. 重大设计决策必须写入对应章节。
3. API 或数据模型发生稳定变化后，同步更新摘要。
4. guided_template 规则变化必须同步更新“guided_template 核心系统”章节。
5. 新增实验必须同步更新“教学实验体系”章节。
6. UI 基线变化必须同步更新“UI 与产品设计约束”章节。
7. 文档更新应使用清晰标题和短段落，避免把聊天记录原样堆入。
8. 若某条内容来自阶段性假设，应标明“待验证”。

## 16. 内容来源说明

### 来自工程平台版

- 工程结构。
- 页面结构。
- API 契约。
- 前后端目录。
- 用户体系。
- UI 设计约束。
- 后端分层。
- 数据模型。
- 管理后台。
- 教师端。
- 学生端。
- 产品结构。
- 项目约束。

### 来自教学实验版

- guided_template 架构与核心定位。
- 教学实验体系。
- 分步教学模式。
- 实验1至实验6。
- 数据分析课程设计。
- Python 沙盒机制。
- MySQL 教学体系。
- 财务专业学生定位。
- “不是培养程序员”的产品边界。
- 数据驱动实验配置。
- 实验参数化设计。
- 引导式模板实验设计。
- 回归分析与关联分析实验。
- 教学业务逻辑。

### 来自当前仓库事实

- 后端 FastAPI、SQLAlchemy、MySQL 分层。
- 前端 Vue 3、Vite、Monaco Editor 技术栈。
- 已存在的 API 摘要。
- `experiments` 的 `native_editor / guided_template` 模式。
- `template_schema / code_template / import_config` 等 guided_template 字段。
- 提交批阅字段与学生导入规则。
- AGENTS 设计约束。

## 17. 跨设备协作约定

为了让不同设备上的 Codex 保持同一份上下文，仓库协作时遵循以下约定：

1. 共享集成分支使用 `dev`。
2. `main` 用于确认版本和服务器部署。
3. 新设备接入时先同步最新远程，再开始新任务。
4. 每个任务优先使用独立功能分支，避免多台设备同时改同一组文件。
5. `README.md`、`AGENTS.md`、`PROJECT_CONTEXT.md` 视为共享上下文，更新时尽量一起维护。
6. `.env`、依赖缓存、虚拟环境和构建产物保持本地化，不纳入版本控制。
7. 遇到冲突时，以远程最新状态为准，在功能分支上解决后再同步回 `dev`。
8. 使用这个聊天进行 Git 自然语言协作时，默认先检查状态，再执行提交、合并或推送，不直接跳过检查步骤。
