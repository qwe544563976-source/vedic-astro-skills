# Prashna 三档判定 Rubric + 拒绝式清单

> **用途**：主判读 Step 5 三档结论(✓成 / ~悬 / ✗不成) 的判据锚点。
> **配合**：Step 1 定 significators → Step 2 五组关系 → Step 3 Moon 动向 → Step 4 择时 → 本表定档。
> **纪律**：三档触发条件是"必要事实清单"，禁止自造中间档、禁止在主证据不齐时勉强下"成"档。

---

## 1. ✓ 成 · 触发条件（多满足 = 更硬）

必要基础(至少 3 条满足)：

1. **Lagna 主 ↔ 相关宫主/事件 Karaka 至少一组接触**（graha drishti / mutual drishti / parivartana / 合宫；整宫落点判定，无 orb）
2. **Moon ↔ 相关宫主/事件 Karaka 至少一组接触**（Moon 是提问盘核心动因，Moon 不触 = 心念未到 = 事难成）
3. **事件 Karaka 状态健康**：`dignity` ∈ {入旺、入庙、入自境、入友方}；非燃烧；非落陷；非死敌
4. **相关宫主落点合意**：落 Kendra(1/4/7/10) 或 Trikona(1/5/9)；避 Dushtana(3/6/8/12)
5. **Moon 无 Void**（Chandra Kriya 判定非空亡；见 `resources/moon-policy.md`）
6. **Vimshottari Dasha 段有匹配**：当前或近期 Dasha/Antar 段的宫主/Karaka 与本题 significator 群有身份重合
7. **SAV ≥ 30**（相关宫；从「宫位映射」表读，SAV 铁规格式 `N宫(Sign)SAV=X`）

**加权**：
- 有 Raja Yoga / Dhana Yoga 触及相关宫或其主 → **成**档更硬
- Jupiter(良吉) graha drishti 触及相关宫主 → **成**档更硬
- Moon 满盈期(shukla paksha 后半，接近满月) → **成**档更硬（Prashna Marga 传统）

---

## 2. ~ 悬 · 边界特征

出现下述任一 = 悬档（除非同时有强救援把它推入成/不成）：

- 主要接触**存在但强度不足**：仅 graha drishti 单向、无 mutual、无 parivartana；或接触方之一落陷/燃烧
- Karaka 尊贵度**中性/落陷**但仍有 graha drishti 救援
- **时间窗超 2 年**：相关 Dasha 段在遥远未来 → 事非当下能定
- **SAV 边界值**（23-29）：不主结论，仅作补充
- 相关宫主**落 Dushtana 但有救援**（如与 Yoga karaka 有 mutual drishti）
- **Moon 有 graha drishti 但无 mutual**：心念到位但事件未闭环
- 用户问的是"能否 XX" 但盘只能答出"XX 会发生但不是你想的形式"

**判读表述**：给"悬"档时必须写清楚"卡在哪一环、需要什么额外条件才能推入成"。禁止只写"目前不明朗"的敷衍。

---

## 3. ✗ 不成 · 拒绝式清单（任一触发即拒）

Prashna Marga 传统拒绝式，任一条命中 = 直接判"不成"：

1. **Moon Void of Course**（吠陀 Chandra Kriya 判定空亡）— 心念断线，事无载体
2. **Lagna 主 & Moon 均落 Dushtana(3/6/8/12) 且无救援** — 提问者本身与心念都不在事的位置
3. **相关宫主 与 事件 Karaka 完全相离**（无任何 graha drishti / mutual / parivartana / 合宫；整宫无接触）
4. **事件 Karaka 双弱**：落陷 + 燃烧（距 Sun ±8° 内）
5. **Moon 在最后一个 pada 且下一个 nakshatra 主是 6/8/12 宫主** — 事往阻碍方向走
6. **相关宫主处 Gandanta**（Cancer-Leo / Scorpio-Sagittarius / Pisces-Aries 星座交界±30′内 的转折带）— 事在断裂带
7. **Lagna 与 Moon 都无良吉 graha drishti**（Jupiter/Venus/Mercury 都不照）— 事无扶助
8. **提问者迟疑不定 / 就同一问题反复起盘** — 提问盘失效（"心念不定，盘不可信" — Prashna Marga 明训）
9. **相关宫主与 Karaka 均落 6 宫或 8 宫且无 Yoga 救援** — 事进阻碍/突变位
10. **本命交叉启用时，本命 Dasha 与 Prashna 时间窗严重打架** — 承 SKILL.md §可选本命交叉硬约束 (本命裁决)

---

## 4. 时间窗判读细则

给窗口不给点。三条判据的读法：

### 4.1 Vimshottari Dasha 段（主判据）
- 找到**相关宫主的 Dasha/Antar 段**：从今日起到未来 5 年内是否有其段
- 找到**事件 Karaka 的 Dasha/Antar 段**：同上
- 两者段**重合期** = 事件时间窗核心（若两者 Antar 段有 3 个月以上重合 → 高概率触发窗）

### 4.2 Moon 换 Nakshatra 触发（补判据）
- Moon 当前 Nakshatra 剩余度数 → 换段时刻可算(约每 27 小时换一个 Nakshatra；SKILL.md `moon_next_contact` 字段给)
- 换段后 Moon 触及的行星 → 事件启动信号（若换段后立刻触及事件 Karaka → 短期启动窗）

### 4.3 Graha Drishti 触发日（细化判据）
- 何时相关宫主的 graha drishti 触及事件 Karaka（用 Dasha 段+过运回避机制估算，禁用 orb）
- 触发日 = 事件启动/成/爆的候选点

**输出格式**：
- 主窗口：`YYYY 年 M-M 月，X Dasha 内 Y Antar 期间`
- 辅窗口：`YYYY-MM-DD 前后（Moon 换 <Nakshatra>）`
- 兜底：`未来 5 年内未见清晰窗口 → 判读改"悬"或"不成"，禁强给远窗`

---

## 5. 自检清单（下三档结论前必核）

- [ ] 主证据一句话能说清吗？说不清 → 挡在"悬"档，禁强推"成"
- [ ] 拒绝式 10 条逐条核过吗？任一命中即"不成"，禁自 override
- [ ] SAV 从「宫位映射」表读的吗？格式对吗？(N宫(Sign)SAV=X)
- [ ] 时间窗给的是**窗口**不是**点**吗？
- [ ] 全流程未引 Tajika/KP/orb/applying 判据吗？
- [ ] 若开启本命交叉：本命 Dasha vs Prashna 时间窗有无严重打架？(打架则本命裁决 → 落"不成"或"悬")
