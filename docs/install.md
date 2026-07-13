# Install manual — Agent Evaluation Layer (for the AI agent to read)

> **You are an AI coding agent (Claude Code, Cursor, etc.) reading this file to
> install the `agent-evaluation-layer` skill for your user. Follow these steps in
> order. Report the *real* command output back — never claim success you didn't verify.**
>
> **你是一个 AI 编程助手，正在阅读本文件来为用户安装 `agent-evaluation-layer` 技能。
> 请按顺序执行，把命令的真实输出汇报给用户，不要谎报没验证过的成功。**

Repository: `https://github.com/pmgwee/Ai-Agent-Evaluation-Layer`

This layer is **manual**: after install, the user triggers it by typing **`/agent-evaluation-layer`**
(the skill's folder name). It does not run in the background. Installing is just
copying **one folder** — there is no command file, and **nothing is added to
`.claude/commands/`**. / 本评估层**手动**：安装后由用户输入 **`/agent-evaluation-layer`**（skill 的
文件夹名）触发，不在后台运行。安装只是复制**一个文件夹**，没有 command 文件，
**`.claude/commands/` 里什么都不会多**。

---

## Step 1 — Ask one question / 先问一个问题

**Install globally or for one project?** / **装成全局还是单项目？**
- **Global** → skill in `~/.claude/skills/agent-evaluation-layer/` — works in every project on this
  machine. (Recommended.) / **全局** → `~/.claude/skills/agent-evaluation-layer/`，本机所有项目可用。（推荐）
- **Project** → skill in `<project>/.claude/skills/agent-evaluation-layer/` — ships with that one
  repo. / **单项目** → `<project>/.claude/skills/agent-evaluation-layer/`，只随该仓库。

Wait for the answer. / 等待回答。

---

## Step 2 — Check prerequisites / 检查前置条件

```bash
git --version
python3 --version    # or: python --version  (Python 3.7+; only needed for the optional probe.py health check)
```

`probe.py` uses only the standard library — no `pip install`, and it is optional
(`/agent-evaluation-layer` scaffolds the log itself). / `probe.py` 只用标准库、无需 `pip install`，
而且是可选的（`/agent-evaluation-layer` 自己会建 log）。

---

## Step 3 — Get the files / 获取文件

```bash
git clone https://github.com/pmgwee/Ai-Agent-Evaluation-Layer.git /tmp/ael
# or download+unzip:
# curl -L -o /tmp/ael.zip https://github.com/pmgwee/Ai-Agent-Evaluation-Layer/archive/refs/heads/main.zip
# unzip -o /tmp/ael.zip -d /tmp/ael-zip   # skill at .../Ai-Agent-Evaluation-Layer-main/skills/agent-evaluation-layer
```

---

## Step 4 — Copy the skill folder into place / 把技能文件夹复制到位

This is the whole install. / 这就是全部安装。

**Global / 全局:**

```bash
mkdir -p ~/.claude/skills
cp -R /tmp/ael/skills/agent-evaluation-layer ~/.claude/skills/
```

```powershell
New-Item -ItemType Directory -Force -Path "$HOME\.claude\skills" | Out-Null
Copy-Item -Recurse -Force "$env:TEMP\ael\skills\agent-evaluation-layer" "$HOME\.claude\skills\"
```

**Project / 单项目** (replace `<project>`):

```bash
mkdir -p <project>/.claude/skills
cp -R /tmp/ael/skills/agent-evaluation-layer <project>/.claude/skills/
```

Confirm the folder landed at `.claude/skills/agent-evaluation-layer/` (containing `SKILL.md`). Report
the real result. / 确认文件夹到了 `.claude/skills/agent-evaluation-layer/`（里面有 `SKILL.md`）。汇报真实结果。

---

## Step 5 — Tell the user how to use it / 告诉用户怎么用

That's the whole install — the skill is invoked by its folder name, so no command
file was created. From now on, in Claude Code:
安装到此结束——skill 靠文件夹名触发，没有生成任何 command 文件。今后在 Claude Code 里：

- **First time in a project:** type `/agent-evaluation-layer` → it creates
  `.agent-eval/EVALUATION_LOG.md` (a dated, append-only history — not a rules
  file). / **某项目第一次**：输入 `/agent-evaluation-layer` → 它会创建
  `.agent-eval/EVALUATION_LOG.md`（一个带日期、只增不改的历史文件，不是规则文件）。
- **Any time after:** `/agent-evaluation-layer <what to record>` — e.g. `/agent-evaluation-layer fixed the rate-limit
  retry bug` or `/agent-evaluation-layer v2: added Stripe checkout`. It appends a dated memory entry
  and **stages** `.agent-eval/` — it never commits or pushes; you review and commit yourself. / **之后任意时候**：`/agent-evaluation-layer <要记录的内容>`，它会追加一条
  带日期的记忆并**暂存** `.agent-eval/`——它绝不 commit 或 push，由你自己 review 后提交。

The skill stages `.agent-eval/` for you; **you** commit it so the memory travels with the repo. / skill 会帮你暂存 `.agent-eval/`，**你自己**提交，让记忆随仓库流转。

---

## What this layer will NOT do / 这个评估层不会做什么

By design it maintains **one** file and stays out of the host agent's way. It never
creates a `SPEC.md` or any "current rules" file, never edits `CLAUDE.md` (your own
docs stay the source of truth for current rules), never adds anything to
`.claude/commands/`, and never installs hooks or session automation. Its
`disable-model-invocation: true` flag means the model never auto-runs it — only the
user does, by typing `/agent-evaluation-layer`. So it can be added to any repo — including one already
governed by a `CLAUDE.md` — with zero risk to the coding agent's behavior. / 按设计它
只维护**一个**文件，绝不干扰宿主 agent：绝不创建 `SPEC.md` 或任何「当前规则」文件、绝不
改写 `CLAUDE.md`（当前规则以你自己的文档为准）、绝不往 `.claude/commands/` 加东西、绝不装
hook 或 session 自动化。它的 `disable-model-invocation: true` 意味着模型永不自动运行它——
只有用户输入 `/agent-evaluation-layer` 才触发。因此可以安全地加进任何仓库——包括已经有 `CLAUDE.md` 的项目——
对 coding agent 的行为零风险。
