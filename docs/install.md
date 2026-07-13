# Install manual — Agent Evaluation Layer (for the AI agent to read)

> **You are an AI coding agent (Claude Code, Cursor, etc.) reading this file to
> install the `agent-evaluation-layer` skill for your user. Follow these steps
> in order. Do not skip the questions. Report the *real* command output back to
> the user — never claim success you didn't verify.**
>
> **你是一个 AI 编程助手（Claude Code、Cursor 等），正在阅读本文件来为用户安装
> `agent-evaluation-layer` 技能。请按顺序执行以下步骤，不要跳过提问环节。把命令的
> 真实输出汇报给用户，不要谎报没有验证过的成功。**

Repository: `https://github.com/pmgwee/Ai-Agent-Evaluation-Layer`

---

## Step 1 — Ask the user two questions / 先问用户两个问题

1. **Global or project-scoped install?** / **全局安装还是单项目安装？**
   - **Global** → the skill goes in `~/.claude/skills/` and is available in every
     project on this machine. / **全局** → 技能装到 `~/.claude/skills/`，本机所有项目可用。
   - **Project** → the skill goes in `<project>/.claude/skills/` and ships with
     that repo. / **单项目** → 技能装到 `<项目>/.claude/skills/`，随该仓库一起分发。

2. **Which project gets the evaluation layer initialized first?** / **先给哪个项目
   初始化评估层？** (the `.agent-eval/` memory folder is created *inside a
   project*, separately from where the skill itself lives / `.agent-eval/` 记忆目录
   是建在**某个具体项目内**的，和技能本身的安装位置分开。)

Wait for the answers before continuing. / 得到回答后再继续。

---

## Step 2 — Check prerequisites / 检查前置条件

Run and confirm each is present. / 逐一确认：

```bash
git --version        # need git / 需要 git
python3 --version    # or: python --version  (need Python 3.7+ for probe.py)
```

If Python is missing the skill still works (the loop is instructions the agent
follows) — only `probe.py` needs Python. Tell the user if it's absent.
如果没有 Python，技能仍可使用（循环是给 agent 读的说明）——只有 `probe.py` 需要
Python。若缺失请告知用户。

---

## Step 3 — Get the files / 获取文件

**Option A — git clone (recommended) / 方案 A：git clone（推荐）**

```bash
git clone https://github.com/pmgwee/Ai-Agent-Evaluation-Layer.git /tmp/ael
```

**Option B — download ZIP / 方案 B：下载 ZIP**

```bash
curl -L -o /tmp/ael.zip https://github.com/pmgwee/Ai-Agent-Evaluation-Layer/archive/refs/heads/main.zip
unzip -o /tmp/ael.zip -d /tmp/ael-zip
# the skill will be at /tmp/ael-zip/Ai-Agent-Evaluation-Layer-main/skills/agent-evaluation-layer
```

---

## Step 4 — Copy the skill into place / 把技能复制到位

Pick ONE target based on the Step 1 answer. / 根据第 1 步的回答二选一。

**Global / 全局:**

```bash
# macOS / Linux
mkdir -p ~/.claude/skills
cp -R /tmp/ael/skills/agent-evaluation-layer ~/.claude/skills/
```

```powershell
# Windows PowerShell
New-Item -ItemType Directory -Force -Path "$HOME\.claude\skills" | Out-Null
Copy-Item -Recurse -Force "$env:TEMP\ael\skills\agent-evaluation-layer" "$HOME\.claude\skills\"
```

**Project-scoped / 单项目** (replace `<project>` / 替换 `<项目路径>`):

```bash
# macOS / Linux
mkdir -p <project>/.claude/skills
cp -R /tmp/ael/skills/agent-evaluation-layer <project>/.claude/skills/
```

```powershell
# Windows PowerShell
New-Item -ItemType Directory -Force -Path "<project>\.claude\skills" | Out-Null
Copy-Item -Recurse -Force "$env:TEMP\ael\skills\agent-evaluation-layer" "<project>\.claude\skills\"
```

Confirm the copy / 确认复制成功:

```bash
ls <target>/agent-evaluation-layer      # expect: SKILL.md  templates/  reference/  scripts/
```

---

## Step 5 — Initialize the evaluation layer in the chosen project / 在所选项目里初始化评估层

From inside (or pointing at) the project chosen in Step 1: / 针对第 1 步选定的项目：

```bash
python3 <skill>/scripts/probe.py --init --dir <project-root>
```

`<skill>` is where you copied it (e.g. `~/.claude/skills/agent-evaluation-layer`).
This creates `<project-root>/.agent-eval/SPEC.md` and `EVALUATION_LOG.md` from the
templates (it will not overwrite files that already exist).
这会从模板创建 `<项目>/.agent-eval/SPEC.md` 和 `EVALUATION_LOG.md`（不会覆盖已存在的文件）。

---

## Step 6 — Probe and report REAL output / 运行 probe 并汇报真实输出

```bash
python3 <skill>/scripts/probe.py --dir <project-root>
```

Paste the actual report to the user. A freshly initialized layer will show
warnings about unfilled `<placeholders>` — that's expected until the Spec is
filled in. / 把真实报告贴给用户。刚初始化的评估层会因为未填写的 `<占位符>` 报
warning，这是正常的，填写 Spec 后即可消除。

Exit codes / 退出码: `0` healthy / 健康 · `1` not initialized or missing sections /
未初始化或缺少章节 · `2` warnings under `--strict` / `--strict` 下有 warning。

---

## Step 7 — Fill in the Spec and write Entry 1 / 填写 Spec 并写下第 1 条记录

Open `<project-root>/.agent-eval/SPEC.md`, fill in **Purpose**, **Source of
Truth**, initial **Rules (R1..)**, and the **Self-Review Rubric** (use
`reference/rubric.md` as a menu). Then write **Iteration Log Entry 1** in
`EVALUATION_LOG.md` and commit:
打开 `SPEC.md`，填写 Purpose、Source of Truth、初始 Rules、Self-Review Rubric（可参考
`reference/rubric.md`）。然后在 `EVALUATION_LOG.md` 写下第 1 条 Iteration Log 记录并提交：

```bash
cd <project-root>
git add .agent-eval && git commit -m "chore: install agent evaluation layer"
```

Re-run the probe to confirm the warnings clear. / 再跑一次 probe 确认 warning 消失。

---

## Done — how the layer is used from now on / 完成——之后如何使用

The skill triggers automatically. On every future task in a project that has a
`.agent-eval/` folder, the agent should: **(1)** read `SPEC.md` + recent log
entries at the start, **(2)** do the work per the rules, **(3)** run the rubric,
**(4)** append a dated Iteration Log entry, **(5)** update the backlog, and
**(6)** commit `.agent-eval/`. See the skill's `SKILL.md` for the full loop.

技能会自动触发。今后在任何带 `.agent-eval/` 的项目里，agent 都应：**(1)** 开始时先读
`SPEC.md` 和最近的记录，**(2)** 按规则做事，**(3)** 跑 rubric，**(4)** 追加一条带
日期的 Iteration Log，**(5)** 更新 backlog，**(6)** 提交 `.agent-eval/`。完整循环见
技能的 `SKILL.md`。
