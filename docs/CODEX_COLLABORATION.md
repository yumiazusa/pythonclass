# Codex 协同开发指南

这份文档用于约定如何在不同设备上的 Codex 之间协同开发同一个仓库。目标很简单：每台设备看到的项目状态尽量一致，改动尽量可追踪，冲突尽量可控。

## 1. 基本前提

- 这个仓库已经是 Git 仓库，并且已经配置了远程 `origin`。
- 共享开发分支使用 `dev`。
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

## 6. 冲突处理

如果冲突发生，推荐顺序是：

1. 先拉取最新远程分支。
2. 在功能分支上解决冲突。
3. 重新检查运行结果。
4. 再提交并推送。

不要直接在不同设备上“各改各的然后硬推”，那样最容易把上下文打散。

## 7. 本仓库的共享上下文

当前项目里最值得两个设备一起对齐的文件是：

- `AGENTS.md`：设计和协作约束
- `PROJECT_CONTEXT.md`：长期主上下文
- `README.md`：启动和协作入口

如果后续增加新的共享规则，优先补到这些文件里，而不是只写在某一台设备的本地笔记中。
