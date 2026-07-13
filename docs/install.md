# Install manual — Agent Evaluation Layer (for the AI agent to read)

> **You are an AI coding agent (Claude Code, Cursor, etc.) reading this file to
> install the `agent-evaluation-layer` skill for your user. Follow these steps in
> order. Report the *real* command output back — never claim success you didn't
> verify.**
>
> **你是一个 AI 编程助手，正在阅读本文件来为用户安装 `agent-evaluation-layer` 技能。
> 请按顺序执行，把命令的真实输出汇报给用户，不要谎报没验证过的成功。**

Repository: `https://github.com/pmgwee/Ai-Agent-Evaluation-Layer`

This layer is **manual by default**: after install, the user triggers it with the
**`/eval`** command. It does not run in the background.
本评估层**默认手动**：安装后由用户用 **`/eval`** 命令触发，不在后台运行。

---

## Step 1 — Ask one question / 先问一个问题

**Install `/eval` globally or for one project?** / **`/eval` 装成全局还是单项目？**
- **Global** → skill in `~/.claude/skills/`, command in `~/.claude/commands/` —
  works in every project on this machine. (Recommended.) / **全局** → 本机所有项目可用。（推荐）
- **Project** → skill in `<project>/.claude/skills/`, command in
  `<project>/.claude/commands/` — ships with that one repo. / **单项目** → 只随该仓库。

Wait for the answer. / 等待回答。

---

## Step 2 — Check prerequisites / 检查前置条件

```bash
git --version
python3 --version    # or: python --version  (Python 3.7+ for probe.py)
```

`probe.py` uses only the standard library — no `pip install`. / `probe.py` 只用标准库，
无需 `pip install`。

---

## Step 3 — Get the files / 获取文件

```bash
git clone https://github.com/pmgwee/Ai-Agent-Evaluation-Layer.git /tmp/ael
# or download+unzip:
# curl -L -o /tmp/ael.zip https://github.com/pmgwee/Ai-Agent-Evaluation-Layer/archive/refs/heads/main.zip
# unzip -o /tmp/ael.zip -d /tmp/ael-zip   # skill at .../Ai-Agent-Evaluation-Layer-main/skills/agent-evaluation-layer
```

---

## Step 4 — Copy the skill into place / 把技能复制到位

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

---

## Step 5 — Install the `/eval` command / 安装 `/eval` 命令

`<skill>` is where you copied it (e.g. `~/.claude/skills/agent-evaluation-layer`).

**Global / 全局:**

```bash
python3 <skill>/scripts/probe.py --install-command
```

**Project / 单项目:**

```bash
python3 <skill>/scripts/probe.py --install-command --scope project --dir <project>
```

This drops `eval.md` into the commands folder. Report the exact output. / 这会把
`eval.md` 放进命令目录。请汇报真实输出。

---

## Step 6 — Tell the user how to use it / 告诉用户怎么用

That's the whole install. From now on, in Claude Code:
安装到此结束。今后在 Claude Code 里：

- **First time in a project:** type `/eval` → it creates
  `.agent-eval/EVALUATION_LOG.md` (a dated, append-only history — not a rules
  file). / **某项目第一次**：输入 `/eval` → 它会创建
  `.agent-eval/EVALUATION_LOG.md`（一个带日期、只增不改的历史文件，不是规则文件）。
- **Any time after:** `/eval <what to record>` — e.g. `/eval fixed the rate-limit
  retry bug` or `/eval v2: added Stripe checkout`. It appends a dated memory entry
  and commits `.agent-eval/`. / **之后任意时候**：`/eval <要记录的内容>`，它会追加一条
  带日期的记忆并提交 `.agent-eval/`。

Commit the `.agent-eval/` folder so the memory travels with the repo. / 记得提交
`.agent-eval/`，让记忆随仓库流转。

---

## What this layer will NOT do / 这个评估层不会做什么

By design it maintains **one** file and stays out of the host agent's way. It never
creates a `SPEC.md` or any "current rules" file, never edits `CLAUDE.md` (your own
docs stay the source of truth for current rules), and never installs hooks or
session automation. So it can be added to any repo — including one already governed
by a `CLAUDE.md` — with zero risk to the coding agent's behavior. / 按设计它只维护
**一个**文件，绝不干扰宿主 agent：绝不创建 `SPEC.md` 或任何「当前规则」文件、绝不改写
`CLAUDE.md`（当前规则以你自己的文档为准）、绝不装 hook 或 session 自动化。因此可以安全地
加进任何仓库——包括已经有 `CLAUDE.md` 的项目——对 coding agent 的行为零风险。
