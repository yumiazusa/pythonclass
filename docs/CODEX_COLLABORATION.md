# Codex 协同开发指南

这份文档用于约定如何在不同设备上的 Codex 之间协同开发同一个仓库。目标很简单：每台设备看到的项目状态尽量一致，改动尽量可追踪，冲突尽量可控。

## 1. 基本前提

- 这个仓库已经是 Git 仓库，并且已经配置了远程 `origin`。
- `dev` 用于开发，`main` 用于确认版本和服务器部署。
- `README.md`、`AGENTS.md`、`PROJECT_CONTEXT.md` 是共享上下文，应该一起维护。
- `.env`、虚拟环境、依赖缓存、构建产物保持本地化，不要提交。

## 2. 新设备接入步骤

在新设备上只需要做一次初始化：

```bash
git clone git@github.com:yumiazusa/pythonclass.git
cd pythonclass
git checkout dev
git pull origin dev
```

如果你已经有本地副本，就先检查远程是否一致：

```bash
git remote -v
git status --short --branch
```

## 3. 每次开始工作前

先确认自己站在最新的 `dev` 上：

```bash
git checkout dev
git pull origin dev
```

然后再创建功能分支：

```bash
git checkout -b codex/<task-name>
```

建议分支名尽量短、明确，例如：

- `codex/login-fix`
- `codex/student-list-ui`
- `codex/api-docs-update`

## 4. 工作过程中的规则

- 每个任务尽量只在一个分支上完成。
- 尽量不要让两台设备同时编辑同一个文件的同一部分。
- 改文档、改配置、改代码尽量分批提交，方便审查。
- 每次大改动前后都跑一次 `git status`，确认没有漏掉文件。

推荐顺手检查：

```bash
git status --short
git diff --stat
```

## 5. 提交与同步

完成一小段工作后就提交，不要攒太久：

```bash
git add .
git commit -m "describe the change"
git push -u origin codex/<task-name>
```

如果另一台设备已经推进了 `dev`，当前设备在继续之前先执行：

```bash
git checkout dev
git pull origin dev
```

必要时再把自己的功能分支 rebase 或合并到最新 `dev`。

功能确认后，按下面顺序发布到 `main`：

```bash
git checkout main
git pull origin main
git merge dev
git push origin main
```

## 6. 用自然语言发 Git 指令

你可以直接在聊天里用自然语言下达 Git 目标，我会先检查当前状态，再决定是否需要提交、合并或推送。

推荐表达方式：

- “检查当前改动，能提交就提交到 `dev` 并推送。”
- “把 `dev` 合并到 `main`，然后推送发版。”
- “先别动代码，只检查现在是不是适合发版。”
- “帮我确认服务器应该拉哪个分支。”

默认理解规则：

1. 如果你只是说“提交”或“推送当前改动”，默认先看 `dev`。
2. 如果你说“发版”或“服务器可用版本”，默认把 `dev` 合并到 `main`。
3. 如果你说“回滚”或“切换版本”，我会先检查是否会影响远程分支，再决定下一步。
4. 如果目标不明确，我会先问一个很短的问题，不擅自猜分支。

## 7. 单账号多设备 Codex

如果你在多台设备上都登录同一个 OpenAI 账号，可以继续同一条 Codex 对话历史，但这不是 Git 的替代品。

推荐方式：

1. 所有设备都使用同一个账号。
2. 在任意设备上继续同一个项目 thread，或者从历史记录里打开同一条对话。
3. 关键协作信息仍然要落到仓库文件里，聊天只用于决策、执行和解释。
4. 切换设备前，先确认当前任务是否已经提交到 Git。
5. 如果任务还在临时讨论阶段，最好先把结论整理成仓库文档，再切设备。

边界说明：

- 同一账号下，不同设备通常可以看到同一条对话历史。
- 但不要把 Codex 当成实时多人共享编辑器。
- 项目状态的权威来源始终是 Git 仓库，而不是聊天记录。

## 8. 冲突处理

如果冲突发生，推荐顺序是：

1. 先拉取最新远程分支。
2. 在功能分支上解决冲突。
3. 重新检查运行结果。
4. 再提交并推送。

不要直接在不同设备上“各改各的然后硬推”，那样最容易把上下文打散。

## 9. 本仓库的共享上下文

当前项目里最值得两个设备一起对齐的文件是：

- `AGENTS.md`：设计和协作约束
- `PROJECT_CONTEXT.md`：长期主上下文
- `README.md`：启动和协作入口
- `main`：确认版本，服务器从这里拉取

如果后续增加新的共享规则，优先补到这些文件里，而不是只写在某一台设备的本地笔记中。
