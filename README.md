# PythonClass

教学型在线 Python 编程平台（第二阶段：后端数据库基础能力）。

## 项目简介

该项目用于《大数据分析技术与基础》课程的在线编程教学场景，当前阶段已完成前后端基础骨架，并在后端接入 MySQL + SQLAlchemy 的基础数据层能力。

## 目录结构

```text
pythonclass/
├── backend/                # FastAPI 后端
├── frontend/               # Vue 3 + Vite 前端
├── docs/                   # 项目文档
├── PROJECT_CONTEXT.md      # 长期主上下文
├── AGENTS.md               # 协作与设计约束
├── .gitignore
└── README.md
```

## 快速启动

### 1. 准备 MySQL

请使用本机或宝塔 MySQL 服务，并创建数据库：

```sql
CREATE DATABASE IF NOT EXISTS edu_code_platform DEFAULT CHARACTER SET utf8mb4;
```

### 2. 启动后端

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.db.init_db
uvicorn app.main:app --reload --port 8081
```

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

## 跨设备协同开发

如果你要在不同设备上的 Codex 之间协同开发，这个仓库建议按下面的方式使用。

### 仓库准备

1. 确保所有设备都连接同一个 GitHub 仓库。
2. `dev` 用于日常开发，`main` 用于确认版本和服务器拉取。
3. 把 `README.md`、`AGENTS.md`、`PROJECT_CONTEXT.md` 一起纳入版本控制，作为共享上下文。
4. `.env`、虚拟环境、`node_modules/` 这类本地文件保持在各自设备上，不要提交。

### 每台设备的标准流程

1. 开始工作前先同步 `dev`：

```bash
git checkout dev
git pull origin dev
```

2. 每个任务单独开分支：

```bash
git checkout -b codex/<task-name>
```

3. 在自己的分支上修改、提交、推送：

```bash
git add .
git commit -m "your message"
git push -u origin codex/<task-name>
```

4. 功能确认后，把 `dev` 合并到 `main`，再推送 `main` 作为确认版本。

### 协同约定

- 一次只让一个设备负责同一组文件，尽量避免并发改同一段代码。
- 先改文档和配置，再动业务代码，便于其他设备快速接手。
- 如果出现冲突，先以远程 `dev` 的最新状态为准，再在功能分支上解决。
- 任何不应该共享的本地信息都放进 `.gitignore`，例如数据库密码、API 密钥和临时缓存。
- 服务器部署只从 `main` 拉取，不直接跟随 `dev`。

更多细节见 [docs/CODEX_COLLABORATION.md](docs/CODEX_COLLABORATION.md)。

### 用这个聊天做 Git 自然语言操作

以后你可以直接在这个聊天里用自然语言说目标，我会先检查仓库状态，再按约定执行。

你可以直接这样说：

- “检查当前改动，能提交就提交到 `dev` 并推送。”
- “把这次确认版本合到 `main`，然后推送。”
- “先别动代码，只检查现在是不是适合发版。”
- “把服务器要用的版本同步到 `main`。”

默认规则：

- 日常开发改动先落到 `dev`。
- 要发版时，把 `dev` 合并到 `main` 并推送。
- 服务器只拉 `main`。
- 任何提交前，我都会先看 `git status`，避免把不该进仓库的文件一起推上去。

### 单账号多设备 Codex

如果你在两台或多台设备上都登录同一个 OpenAI 账号，可以继续同一条 Codex 对话历史，但它不是替代 Git 的同步层。

建议这样用：

1. 两台设备都登录同一个账号。
2. 在任意一台设备上继续同一条 Codex thread，或者从历史记录里打开同一个项目对话。
3. 代码和协作状态仍然以 Git 仓库为准，聊天只负责解释、安排和执行操作。
4. 需要跨设备交接时，把关键结论写进仓库文件，而不是只留在聊天里。

这意味着：

- 同一账号下，设备之间可以看到同一条对话历史。
- 但不要把聊天当成实时共享编辑器。
- 真正的协作真源仍然是 `dev` / `main` 和已经提交到仓库的文件。

## 第二阶段范围

- 提供 MySQL 连接配置与 SQLAlchemy 会话管理
- 提供 users 基础模型与初始化建表脚本
- 提供数据库联通测试接口 `GET /api/users/test`
- 保持模块化目录结构，便于后续扩展用户系统

## 后续扩展方向

- 学生登录与鉴权
- 在线 Python 代码执行与沙箱隔离
- 实验/作业代码保存与版本管理
- 课程文档页、实验页、教师管理页
