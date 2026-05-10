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
uvicorn app.main:app --reload --port 8000
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
2. 所有设备都以 `dev` 作为共享集成分支。
3. 把 `README.md`、`AGENTS.md`、`PROJECT_CONTEXT.md` 一起纳入版本控制，作为共享上下文。
4. `.env`、虚拟环境、`node_modules/` 这类本地文件保持在各自设备上，不要提交。

### 每台设备的标准流程

1. 开始工作前先同步：

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

4. 合并前先回到最新 `dev`，避免设备之间互相覆盖。

### 协同约定

- 一次只让一个设备负责同一组文件，尽量避免并发改同一段代码。
- 先改文档和配置，再动业务代码，便于其他设备快速接手。
- 如果出现冲突，先以远程 `dev` 的最新状态为准，再在功能分支上解决。
- 任何不应该共享的本地信息都放进 `.gitignore`，例如数据库密码、API 密钥和临时缓存。

更多细节见 [docs/CODEX_COLLABORATION.md](docs/CODEX_COLLABORATION.md)。

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
