# 🔱 Vedic Astro Skills v6.2

> AI驱动的吠陀占星分析系统。六个专精Skill协同工作，从星盘数据提取到完整人生审计。
>
> AI-powered Vedic astrology analysis system. Six specialized skills working together — from chart data extraction to complete life audit.

**兼容 Antigravity 和 Claude Code。**

> 💡 **v6.2 是本仓库的开源稳定版本。** 我们的开源初心不变——所有核心功能完整可用。本仓库持续接受社区反馈，修复bug和体验优化。随着前瞻版本的开发验证，成熟的功能也会逐步下放到开源版本。

---

## ✨ v6.2 核心特性

- 🧮 **原生排盘引擎** — vedic-calculator 直接计算星盘，无需JHora软件，输出与JHora 100%一致
- 🔄 **三阶段执行引擎** — Reader分3个独立阶段执行，每阶段独立思考链，杜绝超长思考崩溃
- 🧩 **16条数学校验** — SAV/BAV常量、Ra-Ke对冲、燃烧检测、行星战争、Sandhi/Gandanta、盈月亏月
- 🎯 **需求驱动的数据契约** — 三级清单（🔴关键/🟡重要/🟢可选），缺口自动分析
- 🛡️ **正反双审** — 所有Q&A强制列出支持和制约数据，防止AI偏见
- ⏱️ **时间精度联动** — 出生时间精度不足时自动禁用高敏感分盘，推荐校准
- 📝 **信号驱动验前事** — 弹性3-5条，SOP多维评估 + P1/P5工具箱
- 🕰️ **时间校准引擎** — 5个人生事件逆推出生时间，精度±5分钟，且不强制改时间
- 💍 **婚姻三阶段模型** — L7关系确立 → 9宫法律确认 → 11宫社会公开，替代单点预测
- 📊 **智能报告打包** — 动态文件发现，按前缀自动分组，支持任意分段输出

---

## 🏛️ 六Skill架构

```
用户星盘 (PDF/截图/文本)         用户出生信息 (日期+时间+地点)
    │                                    │
    ▼                                    ▼
┌─────────────┐                 ┌──────────────────┐
│ vedic-reader │                │ vedic-calculator  │
│ 三阶段执行引擎│                │ 原生排盘引擎       │
│ 提取+校验    │                │ 直接计算,无需JHora │
└──────┬──────┘                 └────────┬─────────┘
       │ structured_data.md              │ structured_data.md
       └──────────────┬─────────────────┘
                      ▼
               ┌─────────────┐     ┌────────────────┐
               │  vedic-core  │────▶│ vedic-rectifier │
               │ P1-P12审计   │     │ 5事件逆推±5min  │
               │ 宫位诊断     │     └────────────────┘
               │ 十大板块总结  │
               └──────┬──────┘
                      │ p2a~p5b + appendix
                      ├──────────────┐
                      ▼              ▼
               ┌──────────────┐ ┌───────────┐
               │ vedic-career │ │ vedic-love │
               │ 职业蓝图4Phase│ │ 恋爱时机3Step│
               └──────────────┘ └───────────┘
```

| Skill | 功能 | 触发词 |
|-------|------|--------|
| 📖 **reader** | 星盘数据提取 + 16条数学校验 + 三阶段执行 | "读盘""星盘""印占""占星""看盘" |
| 🧮 **calculator** | 原生排盘引擎，给出生时间即可计算 | "直接排盘""计算星盘""快速排盘" |
| 🔬 **core** | P1-P12行星审计 + D9交叉 + 宫位诊断 + 十大板块 | "开始分析""帮我分析""星盘审计" |
| 💼 **career** | 4Phase职业蓝图（生态位→格局→D9→全维合成） | "分析事业""职业分析""10宫分析" |
| 💘 **love** | 3Step恋爱时机（体质→Dasha窗口→性质定性） | "分析感情""恋爱运势""桃花时机" |
| 📐 **rectifier** | 5事件时间校准，精度±5分钟 | "校准时间""时间矫正""出生时间不准" |

---

## ⚡ 使用指南

### 🔧 环境要求（必装）

> ⚠️ **vedic-calculator 是整个系统的计算基座**，所有 skill 的数据精度都依赖它。请在首次使用前完成以下安装。

| 要求 | 说明 |
|------|------|
| **Python** | 3.8 ~ 3.13（3.14 暂不支持，pysweph 尚无预编译包） |
| **依赖安装** | `pip install -r vedic-calculator/requirements.txt` |

```bash
# 依赖清单 (requirements.txt)
pysweph>=2.10      # 天文计算引擎（Swiss Ephemeris 的 Python 封装）
dashaflow>=0.3     # 尊贵度 + Jaimini Karakas
PyJHora>=4.8.0     # SAV/BAV + 分盘 + Shadbala (含修正层)
pytz>=2024.1       # 时区
```

> 💡 AI 首次运行时会自动检测环境，缺少依赖会自动创建 venv 并安装。通常你不需要手动操作，但**请确保系统已安装 Python 3.8~3.13**。

### 🟢 推荐流程

**方式A：有JHora PDF**
> **Step 1** → 发送星盘PDF/截图，说 **"读盘"**
>
> AI运行 `vedic-reader`：三阶段提取（数据→预分析→验前事）→ 输出 structured_data.md

**方式B：只知道出生时间（无PDF）**
> **Step 1** → 提供出生日期、时间、地点，说 **"直接排盘"**
>
> AI运行 `vedic-calculator`：直接计算星盘 → 输出 structured_data.md

**后续步骤（两种方式相同）：**
> **Step 2** → 说 **"开始分析"** → AI运行 `vedic-core`
>
> **Step 3** → 说 **"分析事业"** 或 **"分析感情"**

```
路径A: 星盘PDF → reader(提取+校验) ─┐
                                     ├→ core(审计) → career/love(专项)
路径B: 出生时间 → calculator(计算)  ─┘
```

### 🟡 快速模式

直接说"分析事业"或"分析感情"也可以。career/love会检测structured_data是否存在：
- 存在 → 直接使用，深度模式
- 不存在 → 提示先运行reader或calculator

### 输入方式（按推荐程度排序）

1. 🧮 **出生时间**（最简单）— 只需日期+时间+地点，calculator直接计算
2. 📝 **文字粘贴** — 从占星软件复制表格直接粘贴，零误差
3. 📄 **PDF上传** — 任何吠陀占星软件导出均可
4. 📸 **截图** — 南印/北印盘均可识别（推荐南印度 Regular）

---

## 📁 项目结构

```
vedic-astro-skills/
├── README.md
├── CHANGELOG.md
├── LICENSE
├── antigravity/skills/          # Antigravity 版本
│   ├── vedic-reader/
│   │   ├── SKILL.md             # 读盘引擎 (1117行)
│   │   └── resources/
│   │       ├── data_contract.md  # 数据契约 (219行)
│   │       └── validation_rules.md # 16条校验规则 (180行)
│   ├── vedic-core/
│   │   ├── SKILL.md             # 核心分析引擎 (875行)
│   │   ├── resources/
│   │   │   ├── p1_p12.md        # P1-P12参数定义 (335行)
│   │   │   ├── house_framework.md # 宫位诊断框架 (211行)
│   │   │   ├── yogas.md         # 格局判定规则 (169行)
│   │   │   ├── qa_rules.md      # Q&A正反双审规则 (188行)
│   │   │   └── report_rules.md  # 报告打包规则 (37行)
│   │   └── scripts/
│   │       └── report_builder.py # HTML报告生成器 (517行)
│   ├── vedic-career/
│   │   └── SKILL.md             # 职业分析引擎 (328行)
│   ├── vedic-love/
│   │   └── SKILL.md             # 恋爱时机引擎 (281行)
│   ├── vedic-calculator/
│   │   ├── SKILL.md             # 排盘引擎 (204行)
│   │   ├── requirements.txt     # Python依赖清单
│   │   └── scripts/
│   │       ├── engine.py        # 主计算引擎 (797行)
│   │       ├── formatter.py     # structured_data输出
│   │       ├── transit.py       # 过运计算
│   │       ├── shadbala_pyjhora.py  # Shadbala修正层 (494行)
│   │       ├── divisional_pyjhora.py # 分盘计算
│   │       ├── ashtakavarga_pyjhora.py # SAV/BAV计算
│   │       └── extras_pyjhora.py # Bhava Bala等
│   └── vedic-rectifier/
│       ├── SKILL.md             # 时间校准引擎 (373行)
│       ├── requirements.txt     # Python依赖清单
│       ├── resources/
│       │   └── event_house_map.md # 事件-宫位映射 (129行)
│       └── scripts/
│           └── time_scan.py     # Lagna/D9扫描计算器 (222行)
└── claude-code/skills/          # Claude Code 版本 (同上)
```

**总计：16个文件 | 6,000+行 | 220KB+**

---

## 📋 版本历史

| 版本 | 日期 | 改动 |
|------|------|------|
| **v6.2** | 2026-06-07 | **vedic-calculator 排盘引擎** + 移植性改造 + PyJHora依赖 |
| v5.0 | 2026-05-22 | 三阶段执行引擎 + 性能优化 + 动态报告打包 |
| v4.9 | 2026-05-14 | 验前事定版: SOP多维评估 + SAV映射铁规 |
| v4.0 | 2026-05-10 | 双通道OCR + 验前事重写 + 时间精度联动 + Rectifier纠偏 |
| v3.0 | 2026-05-06 | 五Skill架构确立 + Rectifier + 正反双审 |

详见 [CHANGELOG.md](CHANGELOG.md)

---

## 🧪 技术体系

- **流派**: KN Rao体系 (Parashari)，Jaimini辅助
- **Ayanamsa**: Lahiri (默认)
- **分盘**: D1/D9/D10/D4/D5 (精度依赖出生时间)
- **校验**: 16条数学校验（SAV=337、BAV行常量、Ra-Ke对冲、燃烧检测等）
- **反偏见**: 正反双审机制 — 禁止只挑用户想听的数据
- **执行引擎**: 三阶段独立思考链（提取→预分析→验前事）

## ☕ Support / 赞赏

If this project helps you, consider buying me a coffee:

如果这个项目对你有帮助，欢迎赞赏支持：

<p align="center">
  <img src="assets/wechat.jpg" width="200" alt="WeChat Pay">
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="assets/alipay.jpg" width="200" alt="Alipay">
</p>

<p align="center">
  <sub>WeChat Pay（微信支付） &nbsp;|&nbsp; Alipay（支付宝）</sub>
</p>

---

## License

MIT
