---
name: vedic-calculator
description: 吠陀占星排盘计算引擎。当用户提供出生时间和地点，需要从零计算星盘数据时触发。输入出生日期、时间、地点，直接输出structured_data.md，跳过JHora排盘和PDF读取流程。当用户提到'直接排盘''计算星盘''不用jhora''快速排盘''算一下'等关键词时触发。也在vedic-reader判断无PDF输入时建议使用。
---

# vedic-calculator: 吠陀占星排盘引擎

> 基于pysweph天文引擎 + dashaflow算法模块，直接从出生时间计算完整星盘数据。
> 输出格式完全兼容vedic-reader的structured_data.md，可直接交给vedic-core分析。

## 前置条件

- Python 3.8 ~ 3.13（pysweph 为 C 扩展，暂无 3.14 预编译包）
- 依赖: 见 requirements.txt（pysweph, dashaflow, PyJHora, pytz）

### 环境自动检测

```
运行前检查依赖是否可用：
  1. 尝试 import pysweph → 成功 → 直接用当前 Python
  2. 失败 → 检查 skill 目录下是否有 venv/
  3. 没有 venv → 自动创建并安装：
     python -m venv <skill目录>/venv
     <skill目录>/venv/Scripts/pip install -r <skill目录>/requirements.txt  # Windows
     <skill目录>/venv/bin/pip install -r <skill目录>/requirements.txt      # Linux/Mac
  4. 有 venv → 直接用 venv 的 Python
```

> ⚠️ `<skill目录>` = vedic-calculator skill 的安装路径，AI 根据实际环境自动填写。

## 使用流程

### Step 1: 收集出生信息

向用户收集：
```
- 出生日期 (YYYY-MM-DD)
- 出生时间 (HH:MM，24小时制)
- 出生地点 (城市名)
- 性别
- 感情状态（可选）
- 时间精度（精确到分钟 / ±15分钟 / ±1小时 / 不确定）
- 时间来源（出生证 / 家人记忆 / 大概回忆 / 未追问）
```

### Step 2: AI转换地理坐标

根据用户提供的城市名，AI直接填写：
- 纬度 (lat)
- 经度 (lon)  
- 时区字符串 (tz_str)

常用参考：
```
北京:     39.9042, 116.4074, "Asia/Shanghai"
上海:     31.2304, 121.4737, "Asia/Shanghai"
广州:     23.1291, 113.2644, "Asia/Shanghai"
成都:     30.5728, 104.0668, "Asia/Shanghai"
台北:     25.0330, 121.5654, "Asia/Taipei"
香港:     22.3193, 114.1694, "Asia/Hong_Kong"
新德里:   28.6139, 77.2090,  "Asia/Kolkata"
孟买:     19.0760, 72.8777,  "Asia/Kolkata"
```

> ⚠️ 中国全境使用 "Asia/Shanghai" (UTC+8)
> ⚠️ 印度全境使用 "Asia/Kolkata" (UTC+5:30)

### Step 3: 运行引擎

在工作目录下创建计算脚本并执行：

```python
import sys, os

# ⚠️ 动态路径：AI根据skill安装位置自动填写
# Antigravity 示例: C:\Users\用户名\.gemini\config\skills\vedic-calculator\scripts
# Claude Code 示例: ~/.claude/skills/vedic-calculator/scripts
SCRIPTS_DIR = r"<vedic-calculator skill 的 scripts 目录绝对路径>"
sys.path.insert(0, SCRIPTS_DIR)

from engine import calculate_full_chart
from transit import calc_transit
from formatter import format_structured_data

# 计算本命盘
chart = calculate_full_chart(
    year=YYYY, month=MM, day=DD, 
    hour=HH, minute=MM,
    lat=LAT, lon=LON, 
    tz_str="TIMEZONE"
)

# 计算当前过运
transit = calc_transit(
    chart['lagna']['sign_idx'],
    chart['planets']['Moon']['sign_idx'],
    "TIMEZONE"
)

# 元信息
meta = {
    'dob': 'YYYY-MM-DD',
    'time': 'HH:MM',
    'place': '城市名',
    'lat': LAT, 'lon': LON,
    'time_precision': '精确到分钟',
    'time_source': '未追问'
}

# 用户信息
user_info = {
    'gender': '男/女',
    'relationship': '单身/恋爱中/已婚'
}

# 生成structured_data.md
md = format_structured_data(chart, transit, meta, user_info)
with open(r"WORKDIR\structured_data.md", 'w', encoding='utf-8') as f:
    f.write(md)
```

执行命令（AI 根据环境自动选择 Python）：
```
# 优先级：skill目录下的venv → 系统Python
# Windows:  <skill目录>\venv\Scripts\python.exe SCRIPT_PATH
# Linux/Mac: <skill目录>/venv/bin/python SCRIPT_PATH
# 都没有venv: python SCRIPT_PATH（需已全局安装依赖）
```

### Step 4: 校验输出

检查生成的structured_data.md：
1. SAV总计 = 337 ✅
2. 行星完整性 = 10颗 ✅
3. Ra-Ke差180° ✅
4. Lagna星座是否合理

### Step 5: 模式选择

structured_data.md 生成后，向用户输出：

```
✅ 排盘完成！所有数据已生成（行星/分盘/SAV/Dasha+小运/宫主表/尊贵度/过运…）

📊 Shadbala 精度说明：
   calc 计算精度 >97%（强弱排序与JHora一致），已可直接使用。
   如你有 JHora PDF，可发来补充更精确的 Shadbala 值。

下一步：
  a) 直接进入验前事（推荐）
  b) 发送 JHora PDF 补充 Shadbala
```

- 用户选 a) 或说"直接分析"/"开始" → 触发 vedic-reader（精简模式：跳过提取，直接读 structured_data → 验前事）
- 用户发送 PDF → 从 PDF 文本层提取 Shadbala → 替换 calc 值 → 再触发 reader 验前事


## 输出规格

输出的structured_data.md包含以下数据板块（完全匹配data_contract.md）：

| 板块 | 内容 |
|------|------|
| 元信息 | 出生时间、地点、Ayanamsa、读盘方式 |
| 行星位置 | 10颗行星+Lagna，星座/宫位/度数/逆行 |
| Nakshatra | 全部行星的Nakshatra+Pada |
| Chara Karakas | 8K主表（含Rahu和PiK）+ DK争议 |
| Shadbala | 7颗行星的Rupas/百分比/排名/强弱 |
| SAV | 原始值(按星座) + 宫位映射(按宫位) |
| BAV | 7颗行星×12星座矩阵 |
| Vimsottari Dasha | 9段大运 + 当前/下一大运Antardasha |
| 特殊点位 | AL(Arudha Lagna) + UL(Upapada Lagna) |
| Compound Dignity | Panchadha Maitri（旺/入庙/陷直接确定） |
| 相位关系 | Top 8最重要相位 |
| 宫主表 | 12宫完整 |
| 分盘 | D9/D10/D4/D5 + Vargottama |
| 校验 | 12项自动校验 |
| 过运 | 慢行星过运 + Sade Sati + 双过运 |

## 技术规格

- Ayanamsa: **Lahiri**（固定，不可更改）
- Node模式: **Mean Node**
- 天文引擎: pysweph (Swiss Ephemeris Python binding)
- SAV/BAV: dashaflow.ashtakavarga
- Shadbala: dashaflow.shadbala  
- Dignity: dashaflow.dignity + 旺/入庙/陷前置判断
- Chara Karakas: 8K（含Rahu和PiK）+ DK争议

## 与其他skill的关系

```
路径1（纯calc，推荐）：
  用户给出生信息 → vedic-calculator → structured_data.md → vedic-reader(验前事) → vedic-core

路径2（PDF + calc借力）：
  用户给PDF → vedic-reader(提取出生信息) → vedic-calculator(算所有数据) → reader(验前事) → core

路径3（兜底）：
  用户只给截图/粘贴文本 → vedic-reader(传统提取) → 借力calc补算分盘/SAV → reader(验前事) → core
```

所有路径输出的 structured_data.md 格式完全一致，core 无需区分数据来源。
