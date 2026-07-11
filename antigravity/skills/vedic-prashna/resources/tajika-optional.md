# Tajika 副层 · 判读消费入口（B 类可选启用）

> **定位**：Tajika 派 = 波斯-印度年运体系(Al-Biruni 传入印度化千年，Varshaphala 即用它)。**判据基于 orb applying/separating aspect**——与主体系(Parashari 整宫落点+Graha Drishti)**口径不同**。
> **纪律**：
> - **默认关**。只在用户显式开启时生成。
> - **独立并行主判读、不叠加主结论**。判读单里若引用，必须标注"【Tajika 补充参考·orb 制】"。
> - **与 Parashari 主结论冲突时，以 Parashari 为准**。
> - Rahu/Ketu 不参与(KN Rao 主线口径)。
> - Retro 参与的对跳过(applying/separating 判定不稳)。

---

## 1. 触发条件

用户显式说以下任一 → 建 build 时加 `--enable-tajika`：

- "用 Tajika 看一下"
- "加个年运层" / "加个 Tajika 层"
- "orb 补充参考" / "看看 orb 层"
- "看看 applying/separating"
- "Ithasala 有没有" / "Muthashila 有没有"
- "Moon 有没有 Manau"

**默认不启用**：用户没提 Tajika/Ithasala/applying 等关键词 → 不加开关，不算 Tajika。

---

## 2. 数据契约（读什么）

`structured_prashna.md` 里"## Tajika 补充参考"段固定含 5 个子表：

| 子表 | 含义 |
|---|---|
| Ithasala | 快星向慢星 applying aspect(offset < 0 且 |offset| ≤ orb sum) — "事在应" |
| Ishraga  | 快星已过 exact aspect，separating(offset ≥ 0 且 ≤ orb sum) — "事已过" |
| Muthashila | 0° applying 合相(aspect=0 且 offset<0) — "事将紧密结合" |
| Manau | Moon → 中间星 Y → 目标 X 的光传递(Moon 与 X 无直接 Ithasala 时) |
| skipped_retro | Retro 参与的对(该对跳过) |

每条 Ithasala/Ishraga 记录字段：`fast/slow` 星名 + `aspect_angle`(0/60/90/120/180) + `offset_deg`(有符号，距 exact 的度数) + `orb_sum`(阈值)。

---

## 3. 语义映射（判读时怎么用）

### 3.1 Ithasala 涉及本题 significator → "Tajika 层辅证"

若 Ithasala 记录里的 fast/slow 至少一颗属于本题 significator 集合(Lagna 主 / Moon / 相关宫主 / 事件 Karaka)：
- 判读单里可加一句 **"Tajika 层辅证：<X–Y Ithasala>，距 exact <n>°，方向与主结论一致"** — 但**不改主结论档次**。
- 若 offset 小(<3°) → 事件在**即将触发**的近期窗口
- 若 offset 大(>10°) → Tajika 层信号弱，仅作背景参考

### 3.2 Muthashila（0° 合相 applying）

- Muthashila 若涉及本题 significator → 事在"紧密结合"阶段；判读时可标注但仍以 Parashari 判据为主结论
- Muthashila 的 fast 与 slow 若一颗是 Moon 一颗是事件 Karaka → Tajika 传统里最强的辅证

### 3.3 Ishraga（分离）

- Ishraga 涉及 significator → Tajika 层暗示"事已过"或"高峰已过"
- 与 Parashari 主结论"成"打架时：**以 Parashari 为准**(主体系不用 orb，Tajika 层的"分离"可能只是 orb 内已飞过)
- 与 Parashari 主结论"不成"一致时：可提"Tajika 层与主结论方向一致"作补充

### 3.4 Manau（光传递）

- Moon 通过中间星 Y 传光到目标 X = **Moon 间接接触 X**
- 若 X 是相关宫主/事件 Karaka：判读单可加 "Tajika 层显示 Moon 通过 Y 间接触达 X — 心念与事件建立中转联系"
- Manau 判据在 Prashna Marga 里属于"次级触发"，不作主结论

### 3.5 Skipped Retro

- 只作说明性列出，判读单里不引用

---

## 4. 判读单里的引用位置

**唯一允许位置**：判读单末尾单独一节 `§六 Tajika 补充参考`(如果启用了)。

**模板**：

```markdown
## 六、Tajika 补充参考（orb 制副层）

> 本节仅在用户开启 Tajika 副层时出现；与主判读独立并行、不叠加主结论。

**Tajika 层观察**：
- Ithasala 涉及本题 significator: <X–Y, 距 exact n°>
- Muthashila: <A–B, 距 exact n°>
- Manau: Moon → <Y> → <X>

**与主判读关系**：[方向一致 · 补充证据] / [方向冲突 · 忽略，以主判读为准]

**语义**：<白话解读，标注是 orb 层参考，不改主结论档次>
```

**禁做**：
- ❌ 把 Tajika 结论写进判读单 §一 主证据
- ❌ 用 Tajika 数据改主结论档次(如"Parashari 判悬，但 Tajika 有 Ithasala 所以改成"成"")
- ❌ 在 §二 主时间窗里用 Tajika applying orb 度数 逆推触发日(用 Dasha + Moon Nakshatra 转段，见 SKILL Step 4)
- ❌ 不加"【Tajika 补充参考·orb 制】"字样直接混入解读

---

## 5. 边界情况

### 5.1 全部 Tajika 表都为空

若 Ithasala/Ishraga/Muthashila/Manau 全空(常见于起盘时刻 Moon 处 sign 中间且行星分散)：
- 判读单里明写"Tajika 层无有效接触，本次副层无补充信号"
- 主判读依原样，不受影响

### 5.2 多个 Ithasala 涉及同一 significator

- 优先取 offset 最小(最近 exact)的记录
- 其余按 offset 排序作次级参考

### 5.3 Moon 参与的 Ithasala 与 Chandra Kriya 冲突

- Chandra Kriya 说 Moon Void，但 Tajika 有 Moon–X Ithasala：**以 Chandra Kriya 为准**(Parashari)
- 原因：Chandra Kriya 用整宫口径判空亡，Tajika 用 orb 判 applying — 主体系口径优先

---

## 6. 自检（判读单写完前，Tajika 相关必核）

- [ ] Tajika 段是否只在用户显式启用后才出现？
- [ ] 引用 Tajika 时是否标注"【Tajika 补充参考·orb 制】"？
- [ ] Tajika 结论是否**未改**主结论档次？
- [ ] Tajika 时间窗是否**未替代** Dasha + Moon Nakshatra 转段的主择时？
- [ ] 与主判读冲突时是否**明说**"以 Parashari 为准"？
- [ ] Retro 涉及的对是否在跳过表里、未被误算？
