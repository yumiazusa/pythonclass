# 本地开发接手清单（无虚拟环境）

适用场景：直接使用本机 `python3`，不使用项目内 `.venv`，且暂不做 Git 管理。

## 1. 后端（本机 Python）

在项目根目录执行：

```bash
cd backend
python3 --version
python3 -m app.db.init_db
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8081
```

检查点：

- 终端看到 `Uvicorn running on http://0.0.0.0:8081`
- 打开 `http://127.0.0.1:8081/health` 返回健康状态

## 2. Node 环境补齐（本机缺 node/npm 时）

当前机器未检测到 `node`/`npm`。可选两种方式：

### 方式 A（推荐）：安装 nvm 后装 Node LTS

安装并启用 nvm 后执行：

```bash
nvm install --lts
nvm use --lts
node -v
npm -v
```

### 方式 B：安装 Node 官方 LTS 安装包

安装完成后重新打开终端，执行：

```bash
node -v
npm -v
```

目标版本：`Node >= 18`，`npm >= 9`。

## 2.1 使用 Docker 容器里的 Node（当前环境）

已确认容器信息：

- 容器 ID：`e0c1464ef771`
- Node：`v22.22.0`
- npm：`10.9.4`
- 项目路径（容器内）：`/www/wwwroot/pythonclass`

进入容器：

```bash
docker exec -it e0c1464ef771 /bin/bash
cd /www/wwwroot/pythonclass/frontend
```

安装与启动前端：

```bash
export VITE_PROXY_TARGET=http://host.docker.internal:8081
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

说明：当后端运行在宿主机（你本机 `python3`）时，容器内访问宿主机应使用 `host.docker.internal`，不要使用 `127.0.0.1`。此处端口与后端保持一致（当前为 `8081`）。

在容器内做构建检查：

```bash
cd /www/wwwroot/pythonclass/frontend
npm run build
```

## 3. 前端启动与构建检查

```bash
cd frontend
npm install
npm run dev
```

新终端执行构建检查：

```bash
cd frontend
npm run build
```

检查点：

- `npm run dev` 正常启动（默认 `http://127.0.0.1:5173` 或终端输出地址）
- `npm run build` 成功，无报错退出
- 若使用容器 Node，访问地址以你面板/NAT 映射后的地址为准

## 4. 前后端联调检查

先启动后端 `8000`，再启动前端 `5173`，然后检查：

1. 打开前端页面可进入实验列表页
2. 前端请求 `/api/*` 可被代理到后端（Vite 已配置）
3. 打开浏览器开发者工具，确认无持续性 `401/500` 错误
4. 最少完成一次登录、实验列表加载、代码运行或提交流程

## 5. 常用排查命令

```bash
# 后端依赖是否可导入
cd backend
python3 - <<'PY'
import fastapi, uvicorn, sqlalchemy, pymysql, pandas, openpyxl
print("backend deps ok")
PY

# 前端依赖树与构建
cd frontend
npm ls --depth=0
npm run build
```
