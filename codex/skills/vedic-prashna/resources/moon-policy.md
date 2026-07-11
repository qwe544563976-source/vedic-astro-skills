# Moon 吠陀动向 · 判读消费入口（moon-policy）

> **用途**：SKILL.md 主判读 Step 3 的**唯一消费入口**——把 `calc_moon_vedic.py` 算出的 `chandra_kriya` + `moon_next_contact` 字段映射为判读语义。
> **纪律**：
> - 数据由沙箱内 `scripts/calc_moon_vedic.py` 生成，Prashna 起盘时由 `build_prashna_data.py` 自动追加到 `structured_prashna.md` 里"## Moon 吠陀动向"段。
> - **禁止模型手推 Moon 空亡/换段时刻/换段后接触**——机械可算的字段一律读表，承共享 engine 下沉哲学。
> - **禁止引 VoC(西占)、Tajika applying-separating aspect**——本 policy 全走整宫落点 + Graha Drishti 吠陀口径，无 orb。

---

## 1. 数据契约（读什么）

`structured_prashna.md` 的"## Moon 吠陀动向"段固定含两个子段：

### 1.1 `Chandra Kriya`
| 字段 | 含义 |
|---|---|
| moon_sign / moon_nakshatra / moon_pada / moon_house | Moon 当前定位 |
| moon_nak_lord | Moon 所在 Nakshatra 的主星 = 当前 Vimshottari Dasha 段主 |
| remaining_in_nakshatra_deg / _days_approx | Moon 出当前 Nakshatra 剩余度数与天数 |
| remaining_in_sign_deg / _days_approx | Moon 出当前 Sign 剩余度数与天数 |
| conjunctions | 与 Moon 同 sign 的行星列表（合宫接触） |
| aspecting_planets / aspecting_details | 有 Graha Drishti 触及 Moon 所在 sign 的行星列表与相位角 |
| is_void | Moon 空亡判定（无合宫且无 drishti 触及） |
| void_note | 若 Void，说明触发 judgment-rubric §3 拒绝式 #1 |

### 1.2 `moon_next_contact`
| 字段 | 含义 |
|---|---|
| next_nakshatra_switch.datetime / days_from_query | Moon 换到下一个 Nakshatra 的精确时刻(swisseph 二分) |
| next_nakshatra_switch.new_nakshatra / new_nak_lord | 新 Nakshatra 名 + 主星（= 新 Vimshottari 段主） |
| next_sign_switch.datetime / days_from_query | Moon 换 sign 的精确时刻 |
| next_sign_switch.new_sign / new_house | 新 sign + Lagna 视角新宫 |
| next_sign_switch.new_conjunctions / new_aspecting_details | 换 sign 后 Moon 所在新 sign 的接触集合（用当前 chart 行星位近似，几天内漂移可忽略） |

---

## 2. 语义映射（判读时怎么用）

### 2.1 Void（空亡）→ 拒绝式判据

若 `chandra_kriya.is_void == True`：
- **直接触发 judgment-rubric §3 拒绝式 #1**：Moon 无载体 → **✗ 不成** 档
- 判读单 §一 主证据一句话：**"心念(Moon)在提问的这个 sign 内孤立无援——事无法启动"**
- 判读单 §四建议默认 **"宜避 / 可等下一 Nakshatra 转段再问"**

### 2.2 当前接触集合 → 心念现在指向哪

若 `chandra_kriya.is_void == False`：
- **合宫接触的行星**：Moon 与之最紧密——判读时权重最高
  - 若合宫方是**事件 Karaka** 或 **相关宫主** → **心念直指事件本身**，成的可能性显著上升
  - 若合宫方是 6/8/12 宫主 → 心念被"阻碍/突变/损失"包裹，倾向 ~悬 或 ✗不成
- **Graha Drishti 触及的行星**：次密——按远近相位加权
  - Jupiter/Venus 触及 → 良吉扶助
  - Saturn/Mars 触及 → 阻力/延迟；如果 Karaka 就是 Saturn/Mars 类，反而是"事在推进的自然阻力"
  - Rahu 触及 → **amplify=True**（承 engine 口径，膨胀/迷惑），判读时**必须标注 Rahu 放大**

### 2.3 换 Nakshatra 时刻 → 主择时触发日

`next_nakshatra_switch.datetime` = **主择时候选点**：
- Moon 换 Nakshatra ≈ Vimshottari 段主换段（Ketu→Venus→Sun→Moon→Mars→Rahu→Jupiter→Saturn→Mercury 依 Nakshatra 主定）
- 判读单 §二 主时间窗必引：**"Moon 于 YYYY-MM-DD HH:MM 换入 <Nakshatra>，Vimshottari 转入 <lord> 段"**
- 新段主若与本题 significator（相关宫主/Karaka）同名 → **强触发窗**
- 新段主若与 significator 有 graha drishti/mutual/parivartana → **中触发窗**
- 新段主与 significator 完全无关 → 此换段仅为"心念小转"，不作主时间窗

### 2.4 换 Sign 时刻 + 换后接触 → 心念下一步指向哪

`next_sign_switch.datetime` + `new_conjunctions/new_aspecting_details`:
- 换 sign 后 Moon 所在宫更新 → **Moon 触及集合更新**
- 若换后新接触集合里出现 significator（相关宫主/Karaka）→ 判读单 §二辅助线索必引：**"Moon 于 YYYY-MM-DD 换入 <sign>(新宫 N)，与 <significator> 建立接触"**
- 若换后接触集合仍为空 → Moon 后段依然 Void：判读单 §三风险段必写"心念在换 sign 后仍无支撑，事持续冷淡"

---

## 3. 边界情况

### 3.1 Moon 处 Nakshatra 最后一 pada
- `moon_pada == 4` 且 `remaining_in_nakshatra_deg < 1°`：Moon 极近换段
- 若下一个 Nakshatra 主是 6/8/12 宫主 → **judgment-rubric §3 拒绝式 #5** 触发考虑：事往阻碍方向走
- 判读时明写：**"Moon 距下一 Nakshatra <hh:mm，转入 <lord> 段，方向为..."**

### 3.2 Moon 处 Gandanta（星座交界±30′内的水火转折带）
Cancer-Leo / Scorpio-Sagittarius / Pisces-Aries 三处为传统 Gandanta。
- 若 `moon_sign_idx ∈ {3, 7, 11}` 且 `moon_degree >= 29.5°` → 出宫向 Gandanta 断裂带
- 若 `moon_sign_idx ∈ {4, 8, 0}` 且 `moon_degree < 0.5°` → 入宫从 Gandanta 出来
- **judgment-rubric §3 拒绝式 #6** 触发考虑：事在断裂带 → 判"悬"或"不成"

### 3.3 换 sign 时刻超过 2 天
- 罕见（Moon 每 sign ~2.25 天）；若出现说明起盘输入异常，validate 时告警

---

## 4. 判读单里的引用样例

**§一 主证据行示例**：

> "月亮(Moon)在 <sign> · <nakshatra>，被 <Karaka/相关宫主> 通过 <angle>th 相位照着——心念在事的位置上，事有载体。"

**§二 主时间窗示例**：

> "主窗口：<YYYY-MM-DD HH:MM> Moon 换入 <new_nak>，Vimshottari 从 <当前段主> 转入 <新段主>；这个新段主正是本题相关宫主，事件启动概率显著。"

**§二 辅助线索示例**：

> "约 <days> 天后（<datetime>），Moon 换入 <new_sign>，同时与 <planet> 建立接触——这是次级触发窗口。"

**§三 风险段示例（Void 情形）**：

> "月亮当前空亡（sign 内无合宫、无 graha drishti 触及）——你此刻的问和事本身没形成有效联系，Prashna Marga 传统里这叫'心念断线'，事难以启动。建议：等 <YYYY-MM-DD HH:MM> Moon 换 Nakshatra 后再问，届时接触集合会更新。"

---

## 5. 术语翻译规则（承 SKILL.md 语言风格）

判读单里出现术语必须当场翻译：

| 术语 | 白话翻译 |
|---|---|
| Chandra Kriya | Moon 状态的吠陀口径判定 |
| Moon Void | 月亮空亡=心念孤立=事无载体 |
| Graha Drishti | 行星整宫照射（吠陀相位，无 orb） |
| Nakshatra | 月宿（27 分星宿，Moon 每约 1 天换一个） |
| Vimshottari 段转 | 大运/小运的段落切换 |
| Nakshatra 主(lord) | 该月宿对应的 Dasha 段主 |
| Gandanta | 星座交界的断裂带（水火转折点） |

---

## 6. 自检（判读单写完前，Moon 相关必核）

- [ ] Moon 段的所有字段是否来自 `structured_prashna.md`「## Moon 吠陀动向」段，未手推？
- [ ] `is_void == True` 时是否落到 ✗不成 档（除非本命交叉裁决 override）？
- [ ] 主时间窗是否引用 `next_nakshatra_switch.datetime` 而非凭记忆？
- [ ] Rahu 若触及 Moon，是否明写"amplify=放大"？
- [ ] 术语出现是否当场翻译？
- [ ] 全流程未引 Tajika applying/separating aspect、未引 VoC 西占口径？
