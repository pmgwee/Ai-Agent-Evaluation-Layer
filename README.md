# Ai-Agent-Evaluation-Layer

A universal **Claude skill** that adds a self-improving *evaluation & iteration-
refinement memory* to any agent-built project. You trigger it **manually** with
the **`/eval`** command whenever you want to record something — a bug fix, a
version enhancement, a new rule — and it writes that into durable memory that
survives across sessions **and across different AI agents**. It does **not** run
in the background.

一个通用的 **Claude 技能**，为任何由 AI 构建的项目加上一层会自我进化的
**「评估 + 迭代精炼」记忆**。你用 **`/eval`** 命令**手动**触发它——想记录什么就记录
（修了某个 bug、某个版本的增强、一条新规则），它就把这些写进能跨会话、跨不同 AI agent
存续的持久记忆里。它**不会在后台运行**。

---

## How it works / 工作方式

You run `/eval` at the moments you choose:

- **First run in a project** → it sets up the layer (creates `.agent-eval/`).
- **Later runs** → `/eval fixed the rate-limit retry bug`, `/eval v2: added Stripe
  checkout`, `/eval add "never log secrets" as a rule` → it records that into
  memory and commits.

你在你选择的时刻运行 `/eval`：**第一次**在某项目运行 → 它会建立评估层
（创建 `.agent-eval/`）；**之后每次** → `/eval 修好了限流重试的 bug`、
`/eval v2：加了 Stripe 结账`、`/eval 把「日志里绝不写密钥」加成一条规则` → 它就把
这条记进记忆并提交。

Between runs, nothing happens and no tokens are spent. / 两次运行之间什么都不发生，
也不消耗 token。

---

## What each project gets / 每个项目会得到什么

```
<project>/.agent-eval/
├── SPEC.md            # living rules, rubrics & regulations (versioned)
└── EVALUATION_LOG.md  # append-only memory: feedback, defects, lessons, backlog
```

- **SPEC.md** — *"what are the rules right now?"* (versioned)
- **EVALUATION_LOG.md** — *"why is that a rule, what broke, what did we learn,
  what's next?"* (append-only, searchable)

Committed to the repo, so `git pull` restores full context on any machine, in any
session, for any agent. / 提交进仓库，因此 `git pull` 就能在任何机器、任何会话、任何
agent 上恢复完整上下文。

---

## Install / 安装

### Option A (recommended) — one prompt / 方案 A（推荐）：一句话安装

Paste this to your agent (Claude Code, Cursor, etc.):
把下面这句贴给你的 agent（Claude Code、Cursor 等）：

```
Help me install the agent-evaluation-layer skill:
https://raw.githubusercontent.com/pmgwee/Ai-Agent-Evaluation-Layer/main/docs/install.md
```

`docs/install.md` is written for the agent to read: it copies the skill into
`.claude/skills/`, installs the `/eval` command, and tells you how to use it.
`docs/install.md` 是写给 agent 读的：它会把技能复制到 `.claude/skills/`、安装 `/eval`
命令，并告诉你怎么用。

### Option B — manual / 方案 B：手动安装

```bash
git clone https://github.com/pmgwee/Ai-Agent-Evaluation-Layer.git
# 1) copy the skill (global = all projects on this machine)
cp -R Ai-Agent-Evaluation-Layer/skills/agent-evaluation-layer ~/.claude/skills/
# 2) install the /eval command (global)
python3 ~/.claude/skills/agent-evaluation-layer/scripts/probe.py --install-command
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path "$HOME\.claude\skills" | Out-Null
Copy-Item -Recurse -Force ".\Ai-Agent-Evaluation-Layer\skills\agent-evaluation-layer" "$HOME\.claude\skills\"
python "$HOME\.claude\skills\agent-evaluation-layer\scripts\probe.py" --install-command
```

Then, in any project, just type **`/eval`**. That's it. / 然后在任何项目里输入
**`/eval`** 即可。就这么简单。

---

## Optional: automatic mode / 可选：自动模式

If you'd rather the layer run on **every** iteration without typing `/eval`, turn
on automatic mode (adds a `CLAUDE.md` pointer + `SessionStart`/`Stop` hooks). This
costs a little extra token overhead per session. / 如果你希望它在**每次**迭代都自动
运行、不用输入 `/eval`，可开启自动模式（会加一段 `CLAUDE.md` 指引 +
`SessionStart`/`Stop` 钩子）。这会带来少量每会话的 token 开销。

```bash
python3 <skill>/scripts/probe.py --automate --dir /path/to/project   # turn on
python3 <skill>/scripts/probe.py --disable  --dir /path/to/project   # turn off
```

The Stop reminder can also be silenced anytime with `AGENT_EVAL_ENFORCE=off`.
Stop 提醒也可随时用 `AGENT_EVAL_ENFORCE=off` 关闭。

---

## Health check / 健康检查

```bash
python3 <skill>/scripts/probe.py --dir /path/to/project           # human report
python3 <skill>/scripts/probe.py --dir /path/to/project --json    # machine-readable
python3 <skill>/scripts/probe.py --dir /path/to/project --strict  # warnings -> exit 2
```

No `pip install` needed. / 无需 `pip install`。

---

## Repository layout / 仓库结构

```
Ai-Agent-Evaluation-Layer/
├── README.md
├── LICENSE
├── docs/
│   └── install.md                         # agent-readable install manual (bilingual)
└── skills/
    └── agent-evaluation-layer/
        ├── SKILL.md                        # the method (manual by default)
        ├── commands/
        │   └── eval.md                     # the /eval slash command (manual trigger)
        ├── templates/
        │   ├── SPEC.template.md
        │   ├── EVALUATION_LOG.template.md
        │   └── CLAUDE.snippet.md           # pointer used by optional automatic mode
        ├── reference/
        │   └── rubric.md                   # rubric menu
        ├── hooks/                          # optional automatic mode
        │   ├── agent_eval_hooks.py
        │   └── settings.hooks.example.json
        └── scripts/
            └── probe.py                    # installer / health check / automate / disable
```

---

## License

MIT — see [LICENSE](LICENSE).
