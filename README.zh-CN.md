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

- **第一次**在某项目运行 → 它会建立评估层（创建 `.agent-eval/EVALUATION_LOG.md`）。
- **之后每次** → `/agent-evaluation-layer 修好了限流重试的 bug`、`/agent-evaluation-layer v2：加了 Stripe 结账` → 它就
  追加一条带日期的记录并提交。

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

因为这个评估层不往任何 session 注入内容,所以这个 log **不会自动喂给未来的 agent**。
之后某个 Claude Code session 不会自动知道它存在、也不会自动去读它——除非你:

- **(a)** 当下叫它:*「先看一下 `.agent-eval/EVALUATION_LOG.md`」*,或者
- **(b)** 在**你自己的** `CLAUDE.md` 里加一句,例如:*「debug 前先查
  `.agent-eval/EVALUATION_LOG.md` 里有没有相关的历史事故。」*

**(b)** 是**你自己**写进**你自己**的规则文件,不是 skill 替你注入——既守住「零侵入」
的安全,又让「未来 agent 不重复过去的错」这个价值真正生效。**推荐加上这一句。**
否则这个 log 只在你手动回查、或手动叫 agent 去读的时候才有用。

---

## 什么时候该跑 `/agent-evaluation-layer` —— 实用指南

### 1. 有意义的都记进 Log；当前规则留在你自己的文档里

每次跑 `/agent-evaluation-layer`，都会往 `EVALUATION_LOG.md` 追加一条记录。至于一个教训要不要**升级
成一条持久规则**，取决于 agent 每次都会套用的同一个判断标准：**这件事有没有持久性**
——会不会在别处复发、有没有不显而易见的根因、如果不记下来同样的问题会不会再犯？
如果是，你就把这条规则写进你项目自己的文档（例如 `CLAUDE.md`），日志里只留一条
指向它的带日期指针。如果只是一次性、没有可复用教训的细节，那就只留在这条 Log 记录里。

这是 agent 每次运行时按照这套方法**做出的判断**，不是一个绝对精确的自动分类器
——但整套方法的设计目的，正是让你**不用自己**提前判断「这个够不够格变成规则」。
一个「很小」的修复完全可能配得上一条规则（比如一次因为环境相关的 ICU 行为差异
导致的货币格式不一致——diff 很小，但持久性很高）；反过来，一个「很大」的功能上线，
如果里面没有任何可复用的通用道理，也可能什么规则都不加。

### 2. 检查点(checkpoint)的概念——把判断往后延，不用当下就做

你不需要在修完一个小问题的当下，立刻停下来决定「这值不值得记」。让改动自然
累积就好。等到一个自然的检查点——要切 session 了，或者一个 phase 真的做完、
测完、确认完工了——再跑一次不带参数的 `/agent-evaluation-layer`。它会用 `git log` / `git diff`
扫描上一条记录之后发生的所有事；「记什么」的判断是在**那个时候**才做，而不是要求
你在埋头写代码的过程中分心去想。

### 3. 每条「独立可复现的教训」记一条 entry，不是每个 session 记一条

如果一个检查点一次扫出好几件互不相关、各自都有独立教训的事，不要把它们压缩进
同一条 entry。如果同一个 session 里你修了两个互不相关的缺陷、各自都教会你一件
不同的事，就应该记成**两条**独立的 Iteration Log entry（跑两次 `/agent-evaluation-layer`，或者
一次要求拆成两条）——而不是揉成一条。合并起来的 entry，以后靠日期、关键词、
标签去搜索时会很难精准定位。

### 4. 值得触发一次 `/agent-evaluation-layer` 的检查点

- 要切换到新 session、或要把工作交给别的 agent 之前。
- 一个 phase **真正实现、测试完、确认完工**之后——不是「代码写完」就算。
- 任何一件独立、可复现的教训发生之后立刻记——不要攒到整个 session 结束才一次性
  倒出来；随手记能让每条 entry 保持精简、好搜索。

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

### 方案 A（推荐）：一句话安装

把下面这句贴给你的 agent（Claude Code、Cursor 等）：

```
Help me install the agent-evaluation-layer skill:
https://raw.githubusercontent.com/pmgwee/Ai-Agent-Evaluation-Layer/main/docs/install.md
```

`docs/install.md` 是写给 agent 读的：它会把技能文件夹复制到 `.claude/skills/agent-evaluation-layer/`、
并告诉你怎么用。不会多加任何别的东西。

### 方案 B：手动安装

安装就是复制一个文件夹。skill 靠**文件夹名**（`agent-evaluation-layer`）触发，所以
**没有 command 文件、`.claude/commands/` 里什么都不会多**。

```bash
git clone https://github.com/pmgwee/Ai-Agent-Evaluation-Layer.git
# 把 skill 文件夹复制到位（全局 = 这台机器上所有项目都能用）
cp -R Ai-Agent-Evaluation-Layer/skills/agent-evaluation-layer ~/.claude/skills/
```

Windows PowerShell：

```powershell
New-Item -ItemType Directory -Force -Path "$HOME\.claude\skills" | Out-Null
Copy-Item -Recurse -Force ".\Ai-Agent-Evaluation-Layer\skills\agent-evaluation-layer" "$HOME\.claude\skills\"
```

然后在任何项目里输入 **`/agent-evaluation-layer`** 即可。就这么简单。（只想绑单个 repo,就复制到
`<project>/.claude/skills/agent-evaluation-layer/`。）

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
├── README.md                                # 英文版
├── README.zh-CN.md                          # 中文翻译（本文件）
├── LICENSE
├── docs/
│   └── install.md                           # 给 agent 读的安装手册（双语）
└── skills/
    └── agent-evaluation-layer/               # 放进 .claude/skills/，用 /agent-evaluation-layer 触发
        ├── SKILL.md                          # 方法本体（手动；单文件、无规则文件、无 hook）
        ├── templates/
        │   └── EVALUATION_LOG.template.md    # 项目日志的起始模板
        ├── reference/
        │   └── rubric.md                     # 可选的 eval 时自查清单
        └── scripts/
            └── probe.py                      # 脚手架 / 健康检查（不安装任何东西）
```

---

## License

MIT —— 见 [LICENSE](LICENSE)。
