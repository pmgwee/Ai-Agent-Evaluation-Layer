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

## Step 5 — Initialize the layer AND wire enforcement / 初始化评估层并接入强制执行

From inside (or pointing at) the project chosen in Step 1, run the one command
that scaffolds the memory **and** wires it to run automatically every iteration:
针对第 1 步选定的项目，运行这一条命令：它会创建记忆文件**并**接好「每次迭代自动运行」的开关：

```bash
python3 <skill>/scripts/probe.py --init --with-hooks --dir <project-root>
```

`<skill>` is where you copied it (e.g. `~/.claude/skills/agent-evaluation-layer`).
This does three things / 这条命令做三件事:

1. Creates `<project-root>/.agent-eval/SPEC.md` and `EVALUATION_LOG.md` from the
   templates (won't overwrite existing files). / 从模板创建 `.agent-eval/SPEC.md` 和
   `EVALUATION_LOG.md`（不覆盖已有文件）。
2. Appends a pointer to `<project-root>/CLAUDE.md` so **every** Claude Code
   session auto-loads the instruction to read/update the layer. / 往 `CLAUDE.md`
   追加一段指引，让**每个**会话自动加载「读取/更新评估层」的规则。
3. Installs `SessionStart` + `Stop` hooks into `<project-root>/.claude/settings.json`
   (deterministic reminders). / 把 `SessionStart` + `Stop` 钩子写入
   `.claude/settings.json`（确定性提醒）。

> **Why enforcement?** Skills are *model-invoked* — the agent may under-trigger a
> skill on a plain "add feature X" prompt. The CLAUDE.md pointer + hooks make the
> loop fire reliably without you re-triggering it. / **为什么需要强制执行？** 技能是
> *模型自行调用*的，普通的「加个功能」提示可能不会触发它。CLAUDE.md 指引 + 钩子能让
> 循环稳定触发，无需你每次手动触发。
>
> Prefer files-only (no hooks)? Use `--init` without `--with-hooks`. To add hooks
> later: `python3 <skill>/scripts/probe.py --install-hooks --dir <project-root>`.
> The Stop reminder can be silenced with `AGENT_EVAL_ENFORCE=off`. / 只想要文件、
> 不要钩子？去掉 `--with-hooks`。之后再加钩子用 `--install-hooks`。Stop 提醒可用
> `AGENT_EVAL_ENFORCE=off` 关闭。

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

## Step 7 — Fill in the Spec and write Entry 1 