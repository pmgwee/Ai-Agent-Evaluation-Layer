# Ai-Agent-Evaluation-Layer

**语言:** [English](README.md) · **中文**

一个通用的 **Claude 技能**，为任何由 AI 构建的项目加上一层会自我进化的
**「评估 + 迭代精炼」记忆**。你用 **`/eval`** 命令**手动**触发它——想记录什么就记录
（修了某个 bug、某个版本的增强、一条新规则），它就把这些写进能跨会话、跨不同 AI agent
存续的持久记忆里。它**不会在后台运行**。

---

## 工作方式

你在你选择的时刻运行 `/eval`：

- **第一次**在某项目运行 → 它会建立评估层（创建 `.agent-eval/`）。
- **之后每次** → `/eval 修好了限流重试的 bug`、`/eval v2：加了 Stripe 结账`、
  `/eval 把「日志里绝不写密钥」加成一条规则` → 它就把这条记进记忆并提交。

两次运行之间什么都不发生，也不消耗 token。

---

## 什么时候该跑 `/eval` —— 实用指南

### 1. Log 会记下所有事；只有「有持久性」的才会进 Spec

每次跑 `/eval`，都会往 `EVALUATION_LOG.md` 追加一条记录。至于这条记录**要不要**
同时被升级进 `SPEC.md` 的 Rules 区（并跳版本号），取决于 agent 每次都会套用的
同一个判断标准：**这件事有没有持久性**——会不会在别处复发、有没有不显而易见的
根因、如果不记下来同样的问题会不会再犯一次？如果是，它就会变成一条正式的
版本化规则，以后的迭代会自动遵守；如果只是一次性的细节、没有可复用的教训，
那就只留在这条 Log entry 里，不需要为它去扩充 Spec。

这是 agent 每次运行时按照这套方法**做出的判断**，不是一个绝对精确的自动分类器
——但整套方法的设计目的，正是让你**不用自己**提前判断「这个够不够格变成规则」。
一个「很小」的修复完全可能配得上一条规则（比如一次因为环境相关的 ICU 行为差异
导致的货币格式不一致——diff 很小，但持久性很高，正是值得升级成规则的那种教训）；
反过来，一个「很大」的功能上线，如果里面没有任何可复用的通用道理，也可能一条
新规则都不会加。

### 2. 检查点(checkpoint)的概念——把判断往后延，不用当下就做

你不需要在修完一个小问题的当下，立刻停下来决定「这值不值得记」。让改动自然
累积就好。等到一个自然的检查点——要切 session 了，或者一个 phase 真的做完、
测完、确认完工了——再跑一次不带参数的 `/eval`。它会用 `git log` / `git diff`
扫描上一条记录之后发生的所有事；「只记一笔」还是「升级成规则」的判断,是在
**那个时候**才做，而不是要求你在埋头写代码的过程中分心去想。

### 3. 每条「独立可复现的教训」记一条 entry，不是每个 session 记一条

如果一个检查点一次扫出好几件互不相关、各自都有独立教训的事，不要把它们压缩进
同一条 entry。如果同一个 session 里你修了两个互不相关的缺陷、各自都教会你一件
不同的事，就应该记成**两条**独立的 Iteration Log entry(跑两次 `/eval`，或者
一次要求拆成两条)——而不是揉成一条。合并起来的 entry，以后靠日期、关键词、
标签去搜索时会很难精准定位。

### 4. 值得触发一次 `/eval` 的检查点

- 要切换到新 session、或要把工作交给别的 agent 之前。
- 一个 phase **真正实现、测试完、确认完工**之后——不是「代码写完」就算。
- 任何一件独立、可复现的教训发生之后立刻记——不要攒到整个 session 结束才一次性
  倒出来；随手记能让每条 entry 保持精简、好搜索。

---

## 每个项目会得到什么

```
<project>/.agent-eval/
├── SPEC.md            # 现行的规则、Rubric、规定（版本化）
└── EVALUATION_LOG.md  # 只增不改的记忆：反馈、缺陷、教训、待办
```

- **SPEC.md** —— *「现在的规则是什么？」*（版本化）
- **EVALUATION_LOG.md** —— *「为什么会有这条规则、发生过什么、学到了什么、
  接下来要做什么？」*（只增不改，可搜索）

提交进仓库，因此 `git pull` 就能在任何机器、任何会话、任何 agent 上恢复完整上下文。

---

## 安装

### 方案 A（推荐）：一句话安装

把下面这句贴给你的 agent（Claude Code、Cursor 等）：

```
Help me install the agent-evaluation-layer skill:
https://raw.githubusercontent.com/pmgwee/Ai-Agent-Evaluation-Layer/main/docs/install.md
```

`docs/install.md` 是写给 agent 读的：它会把技能复制到 `.claude/skills/`、安装
`/eval` 命令，并告诉你怎么用。

### 方案 B：手动安装

```bash
git clone https://github.com/pmgwee/Ai-Agent-Evaluation-Layer.git
# 1) 复制技能（全局 = 这台机器上所有项目都能用）
cp -R Ai-Agent-Evaluation-Layer/skills/agent-evaluation-layer ~/.claude/skills/
# 2) 安装 /eval 命令（全局）
python3 ~/.claude/skills/agent-evaluation-layer/scripts/probe.py --install-command
```

Windows PowerShell：

```powershell
New-Item -ItemType Directory -Force -Path "$HOME\.claude\skills" | Out-Null
Copy-Item -Recurse -Force ".\Ai-Agent-Evaluation-Layer\skills\agent-evaluation-layer" "$HOME\.claude\skills\"
python "$HOME\.claude\skills\agent-evaluation-layer\scripts\probe.py" --install-command
```

然后在任何项目里输入 **`/eval`** 即可。就这么简单。

---

## 可选：自动模式

如果你希望它在**每次**迭代都自动运行、不用输入 `/eval`，可开启自动模式
（会加一段 `CLAUDE.md` 指引 + `SessionStart`/`Stop` 钩子）。这会带来少量
每会话的 token 开销。

```bash
python3 <skill>/scripts/probe.py --automate --dir /path/to/project   # 开启
python3 <skill>/scripts/probe.py --disable  --dir /path/to/project   # 关闭
```

Stop 提醒也可随时用 `AGENT_EVAL_ENFORCE=off` 关闭。

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
├── README.md                                # 本文件的英文版
├── README.zh-CN.md                          # 中文翻译（本文件）
├── LICENSE
├── docs/
│   └── install.md                           # 给 agent 读的安装手册（双语）
└── skills/
    └── agent-evaluation-layer/
        ├── SKILL.md                          # 方法本体（默认手动触发）
        ├── commands/
        │   └── eval.md                       # /eval 斜杠命令（手动触发入口）
        ├── templates/
        │   ├── SPEC.template.md
        │   ├── EVALUATION_LOG.template.md
        │   └── CLAUDE.snippet.md             # 自动模式使用的 CLAUDE.md 指引片段
        ├── reference/
        │   └── rubric.md                     # Rubric 选项菜单
        ├── hooks/                            # 可选自动模式
        │   ├── agent_eval_hooks.py
        │   └── settings.hooks.example.json
        └── scripts/
            └── probe.py                      # 安装器 / 健康检查 / 自动开关
```

---

## License

MIT —— 见 [LICENSE](LICENSE)。
