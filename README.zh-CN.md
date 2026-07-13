# Ai-Agent-Evaluation-Layer

**语言:** [English](README.md) · **中文**

一个通用的 **Claude 技能**，为任何由 AI 构建的项目加上一层持久、只增不改的
**迭代历史**——记录项目**为什么**会这样改：缺陷、根因、教训、决策，以及真实的用户反馈。
你用 **`/agent-evaluation-layer`** 命令**手动**触发它，它就把这些写进一个随仓库提交、能跨会话、
跨不同 AI agent 存续的文件里。它**不会在后台运行**。

它只维护**一个文件**，而且**不是规则文件**：项目**当前的规则**依旧以你项目自己的
文档（`CLAUDE.md`、README、ADR）为唯一真相来源——因此永远不会有第二份「当前规则」
文件跟它们悄悄产生矛盾，这个技能做的任何事也不会影响你 coding agent 的行为。

---

## 工作方式

你在你选择的时刻运行 `/agent-evaluation-layer`：

- **第一次** → 创建 `.agent-eval/EVALUATION_LOG.md`。
- **之后每次** → 例:`/agent-evaluation-layer 修好了限流重试的 bug` → 追加一条带日期的记录并提交。

两次运行之间什么都不发生，也不消耗 token。

---

## 它绝不碰什么（为什么可以安全地加进任何项目）

- **没有规则文件。** 它绝不创建 `SPEC.md` 或任何「当前规则」文件。当前规则留在你
  项目自己的文档里，所以两者不可能产生矛盾漂移。
- **绝不改写 `CLAUDE.md`。** 如果出现一条持久规则，日志只记一条带日期的**指针**，
  并提醒你自己把规则写进你的文档——它绝不替你动手写。
- **不装 hook、不做 session 自动化。** 它不往任何 session 注入内容、不拦截任何 turn、
  不改变任何 agent 行为。`/agent-evaluation-layer` 只写 `.agent-eval/EVALUATION_LOG.md` 这一个文件。

---

## 重要:log 的「读回」也是手动的

评估层不注入任何东西,所以**未来的 session 不会自动去读**这个 log。让它发挥作用,二选一:

- **(a)** 当下叫它:*「先看一下 `.agent-eval/EVALUATION_LOG.md`」*,或
- **(b)** 在**你自己的** `CLAUDE.md` 里加一句,例:*「debug 前先查 `.agent-eval/EVALUATION_LOG.md` 里的历史事故。」*

**(b)** 是**你自己**写进**你自己**的规则文件(不是 skill 替你注入),既守住零侵入、又让 log 真正有用。**推荐。**

---

## 什么时候该跑 `/agent-evaluation-layer`

**按「可复用教训」判断,不按大小。** 可能复发、有不显而易见的根因、或未来 agent 会再踩——就记。小修复也能值得一条规则;大上线也可能什么都学不到。一次性琐事(打错字)留在 commit message 就好。

**在检查点跑,不要边改边判断。** 别每改一处就停下来想「这值不值得记」——让改动累积,到一个检查点(见下)再跑一次。不带参数时它会用 `git log`/`git diff` 扫出自上次记录以来的所有改动。

**每条教训记一条,不是每个 session 一条。** 两个互不相关的缺陷 = 两条 entry(更好搜),不要揉成一坨。

**好的检查点:**
- 切换 session / 交接给别的 agent 之前
- 一个 phase **真正实现、测试完、确认完工**之后
- 任何独立、可复现的教训发生之后立刻记

---

## 每个项目会得到什么

```
<project>/.agent-eval/
└── EVALUATION_LOG.md  # 只增不改的历史：为什么改——反馈、缺陷、根因、教训、决策、待办
```

一个文件，随仓库提交，因此 `git pull` 就能在任何机器、任何会话、任何 agent 上
恢复完整历史。它记录的是你的快照文档（`CLAUDE.md`、README、ADR）不会保留的
带日期**历史**——它绝不重述那些文档里已有的当前规则。

---

## 安装

安装 = 把一个文件夹复制进 `.claude/skills/`。skill 靠**文件夹名**(`/agent-evaluation-layer`)运行,所以**没有 command 文件、`.claude/commands/` 里什么都不会多**。(全局 `~/.claude/skills/` = 所有项目;项目 `<project>/.claude/skills/` = 单个 repo。)

**方案 A — 一句话**(贴给你的 agent):

```
Help me install the agent-evaluation-layer skill:
https://raw.githubusercontent.com/pmgwee/Ai-Agent-Evaluation-Layer/main/docs/install.md
```

**方案 B — 手动:**

```bash
git clone https://github.com/pmgwee/Ai-Agent-Evaluation-Layer.git
cp -R Ai-Agent-Evaluation-Layer/skills/agent-evaluation-layer ~/.claude/skills/
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path "$HOME\.claude\skills" | Out-Null
Copy-Item -Recurse -Force ".\Ai-Agent-Evaluation-Layer\skills\agent-evaluation-layer" "$HOME\.claude\skills\"
```

然后在任何项目里输入 **`/agent-evaluation-layer`** 即可。

---

## 健康检查

```bash
python3 <skill>/scripts/probe.py --dir /path/to/project           # 人类可读报告
python3 <skill>/scripts/probe.py --dir /path/to/project --json    # 机器可读
python3 <skill>/scripts/probe.py --dir /path/to/project --strict  # 有警告则 exit 2
```

无需 `pip install`。

---

## 仓库结构

```
Ai-Agent-Evaluation-Layer/
├── README.md · README.zh-CN.md   # 文档（英 / 中）
├── LICENSE                        # MIT
├── docs/install.md                # 给 agent 读的安装手册
└── skills/agent-evaluation-layer/
    ├── SKILL.md                   # 方法本体 —— 用 /agent-evaluation-layer 触发
    ├── templates/EVALUATION_LOG.template.md   # 项目日志的起始模板
    ├── reference/rubric.md        # 可选的 eval 时自查清单
    └── scripts/probe.py           # 脚手架 + 健康检查（不安装任何东西）
```

---

## License

MIT —— 见 [LICENSE](LICENSE)。
