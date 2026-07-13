# Ai-Agent-Evaluation-Layer

A universal **Claude skill** that adds a self-improving *evaluation & iteration-
refinement layer* to any agent-built project. Drop it into any repo and every
iteration compounds in quality instead of resetting each session — enhancements,
fixes, new rules, rubrics, regulations, and real user feedback are captured the
moment they happen and carried across sessions **and across different AI agents**.

一个通用的 **Claude 技能**，为任何由 AI 构建的项目加上一个会自我进化的
**「评估 + 迭代精炼」层**。放进任意仓库后，每一次迭代都会让系统质量不断累积，而不是
每个会话都从零开始——增强、修复、新规则、评分标准（rubric）、规范、真实用户反馈都会
在发生的当下被记录，并在不同会话、不同 AI agent 之间传承。

---

## Why / 为什么需要它

Agents forget. A new session — or a different agent — starts cold and loses the
rules you agreed on, the defects you already fixed, and the feedback you already
gave. This layer makes memory a committed part of the repo, so quality only goes
up.

Agent 会遗忘。新会话或换一个 agent 就会「冷启动」，丢掉你们约定的规则、已经修过的
缺陷、已经给过的反馈。这个层把「记忆」变成仓库里被提交的一部分，让质量只增不减。

---

## What it gives each project / 它给每个项目带来什么

Inside any project, the skill maintains a committed memory folder:

```
<project>/.agent-eval/
├── SPEC.md            # the living rules, rubrics & regulations (versioned)
└── EVALUATION_LOG.md  # append-only memory: feedback, defects, lessons, backlog
```

- **SPEC.md** answers *"what are the rules right now?"* — versioned.
- **EVALUATION_LOG.md** answers *"why is that a rule, what broke, what did we
  learn, what's next?"* — append-only and searchable.

Together they **are** the system's persistent memory. In a git repo they're
committed, so `git pull` restores full context on any machine, in any session,
for any agent.

---

## The loop / 迭代循环

On every task, the agent: **1)** loads the Spec + recent log, **2)** does the
work per the rules, **3)** runs the Self-Review Rubric, **4)** captures user
feedback near-verbatim, **5)** does an *advisory pass* where the system reviews
itself for latent defects and next improvements, **6)** appends a dated
Iteration Log entry (and bumps the Spec if a rule changed), **7)** commits
`.agent-eval/`.

每次任务，agent 会：**1)** 读 Spec + 最近记录，**2)** 按规则做事，**3)** 跑自评
rubric，**4)** 近乎逐字记录用户反馈，**5)** 做一次「系统自审」发现潜在缺陷与下一步
改进，**6)** 追加一条带日期的迭代记录（规则变了就更新 Spec 版本），**7)** 提交
`.agent-eval/`。

---

## Does it run by itself? / 会自动运行吗？

Install and init are **one-time** per project — you don't re-trigger it each
feature. But skills are *model-invoked*, so to make the loop fire **reliably**
every iteration the layer wires itself into the project two ways:

- a **`CLAUDE.md` pointer** (auto-loaded every session), and
- **`SessionStart` + `Stop` hooks** (deterministic; the Stop hook nudges the
  agent to log an iteration when code changed but the log didn't).

`--init --with-hooks` sets both up. After that, just develop normally and the
memory is written progress-by-progress. Silence the Stop nudge anytime with
`AGENT_EVAL_ENFORCE=off`.

安装和初始化对每个项目只需**一次**，不用每个功能都手动触发。但由于技能是*模型自行
调用*的，为了让循环**稳定**在每次迭代触发，评估层会用两种方式接入项目：一段
**`CLAUDE.md` 指引**（每个会话自动加载），以及 **`SessionStart` + `Stop` 钩子**
（确定性执行；当有代码改动却没更新日志时，Stop 钩子会提醒 agent 记录本次迭代）。
`--init --with-hooks` 会一次装好两者。之后正常开发即可，记忆会一步步写入。想关闭
Stop 提醒，设 `AGENT_EVAL_ENFORCE=off`。

---

## Install / 安装

### Option A (recommended) — one prompt / 方案 A（推荐）：一句话安装

Paste this to your agent (Claude Code, Cursor, etc.):
把下面这句贴给你的 agent（Claude Code、Cursor 等）：

```
Help me install the agent-evaluation-layer skill:
https://raw.githubusercontent.com/pmgwee/Ai-Agent-Evaluation-Layer/main/docs/install.md
```

`docs/install.md` is written **for the agent to read**: it asks two questions
(global vs. project? which project gets the layer?), checks prerequisites,
clones/downloads, copies the skill into `.claude/skills/`, runs `probe.py --init`,
then reports the real output.

`docs/install.md` 是**写给 agent 读**的安装手册：先问两个问题（全局还是单项目？给哪个
项目初始化评估层？）→ 检查前置条件 → clone/下载 → 复制到 `.claude/skills/` →
跑 `probe.py --init` → 汇报真实输出。

### Option B — manual / 方案 B：手动安装

```bash
git clone https://github.com/pmgwee/Ai-Agent-Evaluation-Layer.git
# Global:  copy the skill folder to ~/.claude/skills/
cp -R Ai-Agent-Evaluation-Layer/skills/agent-evaluation-layer ~/.claude/skills/
# Project: copy it to <project>/.claude/skills/ instead
```

Then initialize a project's memory folder **and** wire it to run automatically
(creates `.agent-eval/`, appends the `CLAUDE.md` pointer, installs the hooks):

```bash
python3 ~/.claude/skills/agent-evaluation-layer/scripts/probe.py --init --with-hooks --dir /path/to/project
```

Or on Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path "$HOME\.claude\skills