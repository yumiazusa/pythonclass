# edu-code-platform

教学型在线 Python 编程平台（第二阶段：后端数据库基础能力）。

## 项目简介

该项目用于《大数据分析技术与基础》课程的在线编程教学场景，当前阶段已完成前后端基础骨架，并在后端接入 MySQL + SQLAlchemy 的基础数据层能力。

## 目录结构

```text
edu-code-platform/
├── backend/                # FastAPI 后端
├── frontend/               # Vue 3 + Vite 前端
├── docs/                   # 项目文档
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
