# KP 独立判读栈 · 判读消费入口（C 类独立切换）

> **定位**：KP (Krishnamurti Paddhati) = 独立占星体系，用 **sub-lord signify 判事件成败**。
> **纪律**：
> - **默认关**。只在用户显式切换时启用。
> - **与 Parashari 主判读互斥**——启用 KP 后判读走 KP-only 栈；Parashari 主判读段虽在 md 里但判读时忽略。
> - **绝不同时输出为主结论**——判读单顶部明确 "本次判读走 KP 栈"。
> - **技术选型**：Placidus house system(KP 传统) + True Citra ayanamsa(与主盘一致，与 KP 原用 KP ayanamsa 差异<1°) + Vimshottari 比例分 sub。

---

## 1. 触发条件

用户显式说以下任一 → build 时加 `--enable-kp`：

- "用 KP 看这个盘" / "用 KP 判"
- "看看 sub-lord"
- "KP 独立体系"
- "切换到 KP"
- "用 Krishnamurti 派"

**默认策略**：用户没提上述关键词 → 走 Parashari 主判读，不启用 KP。

**特殊约束（互斥）**：如果用户同时说了 Tajika 和 KP，先澄清"要 Parashari 主 + Tajika 副参考，还是切换到 KP 独立栈？"，不能同时启用。

---

## 2. 数据契约（读什么）

`structured_prashna.md` 里"## KP 独立判读栈"段固定含 2 个子表：

### 2.1 `12 宫 Placidus Cusp KP 三主`
| 字段 | 含义 |
|---|---|
| house | 宫号(1-12) |
| cusp | 该 cusp 的度数(星座内 D°MM') |
| sign | Cusp 所在星座 |
| sign_lord | 星座主星 |
| star_lord | Cusp 所在 Nakshatra 的主星 |
| **sub_lord** | Cusp 所在 sub 的主星（KP 判读的核心） |

### 2.2 `行星 KP 三主`
- Lagna + Sun/Moon/Mars/Mercury/Jupiter/Venus/Saturn + Rahu/Ketu
- 每颗给 sign / sign_lord / star_lord / **sub_lord**

---

## 3. KP 判读元流程

**KP 主判据**：**相关宫的 cusp sub_lord signify 哪些宫 → 判事件成败**。

### 3.1 定问题类别对应的 KP 相关宫

（同 `house-karaka-map.md` 里的宫位映射，但 KP 用 Placidus cusp 视角）：
- 问婚 → 7 宫 cusp
- 问事业 → 10 宫 cusp
- 问健康 → 1 宫 + 6 宫 cusp
- 问失物 → 2 宫 cusp
- 问诉讼 → 6 宫 + 7 宫 cusp
- ...

### 3.2 查该 cusp 的 sub_lord

从"12 宫 Placidus Cusp KP 三主"表读 sub_lord。

### 3.3 判 sub_lord 是否 signify 事件正宫

**KP 4-fold significator 简化版**（判 sub_lord 是否代表相关宫）：
1. sub_lord **在**相关宫 (as tenant) → 强 signify
2. sub_lord **是**相关宫的宫主 (sign_lord of cusp) → 中 signify
3. sub_lord 与相关宫主 **共 Nakshatra**（sub_lord 的 star_lord 是相关宫主）→ 弱 signify
4. sub_lord 与相关宫 **在同一 star_lord 下**（sub_lord 的 star_lord 是相关宫的 star_lord）→ 微弱 signify

任一满足即 signify；越强越明确。

### 3.4 结论判定

- 相关宫 cusp sub_lord signify **相关宫本身** → ✓ **成**
- 相关宫 cusp sub_lord signify **6/8/12** (dushtana) → ✗ **不成/损失/阻碍**
- 相关宫 cusp sub_lord signify **中性宫**(无直接支持也无阻碍) → ~ **悬**

**辅助 signify 规则**：
- Rahu/Ketu 在 KP 里是**特殊 agent**：它们的 sub-lord 语义取"其占用星座主星"(即 sign_lord where they sit) 与"其 conjunct 的行星"的合并语义
- 判读时优先取 conjunct 的语义，其次取 sign_lord

---

## 4. 判读单结构（KP 栈专用）

**判读单顶部**必须写：

```markdown
# Prashna 判读单：<问题简述>  [KP 判读栈·独立体系]

> ⚠️ 本次判读走 KP 独立判读栈；与 Parashari 主判读体系不同、不叠加。
> Parashari 段(D1/Karaka/Dasha/graha_drishti/SAV) 数据仍在 md 里，但本判读**忽略**。
```

**结论段结构**（保留三档 + 时间窗 + 建议，但依据换成 KP）：

```markdown
## 一、能不能成? [KP 栈]
**结论**：[✓成 / ~悬 / ✗不成]
**KP 主证据**：相关宫 <N> cusp sub_lord = <X>；<X> signify <哪些宫> → <结论>。

## 二、何时成? [KP 栈]
**主时间窗**：由**当前 Vimshottari 大运/小运的 sub_lord** signify 事件相关宫时触发。
- 大运主 <M> 内、小运主 <A>、Praty 主 <P> 的段落中，sub_lord signify 相关宫 → 事件窗
- 与 Moon transit 换 sub-lord 触发日结合(见 Chandra Kriya 段的 next_nakshatra_switch)

## 三、KP 主证据表
### 3.1 相关宫 cusp 三主
| 宫 | Cusp | Sign | Sign lord | Star lord | **Sub lord** | Signify |
|...|

### 3.2 sub_lord Signify 分析
| Sub lord | 落宫 | 主哪些宫 | Star lord 主哪些宫 | 综合 signify |
|...|

## 四、建议 [KP 栈]
[可作 / 可等 / 宜避] — <一句话理由>
```

**禁做**：
- ❌ 混用 Parashari 的 Chara Karaka / DK / UL / SAV 等做 KP 判据
- ❌ 用 graha_drishti 做 KP 主判据（KP 不用 Parashari 相位；有需要用 KP 的 aspects 请查 KP 专门文献）
- ❌ 判读单同时给 Parashari 和 KP 两套结论（互斥切换 = 二选一）

---

## 5. 边界情况

### 5.1 KP 与 Parashari 结论明显打架
KP 和 Parashari 是不同体系，出现打架是**正常**的：
- 用户开 KP = 承认走 KP 栈的结论
- **不做"综合"** —— 综合就是混体系，违背 C 类独立切换定位

### 5.2 sub_lord 无明确 signify
若 sub_lord 与相关宫、相关宫主、dushtana 都无 signify 关系：
- 判**~悬**档，说明"KP 层此题无强 signify，事的方向不明"
- 建议用户改用 Parashari 主判读或补澄清问题

### 5.3 用户混用 Tajika + KP
- 拒绝同时启用（第 1 节 §触发条件最后一段）
- 让用户二选一：Parashari 主 + Tajika 副 (B 类) vs KP 独立栈 (C 类)

---

## 6. 自检（KP 判读单写完前必核）

- [ ] 判读单顶部是否标注"【KP 判读栈·独立体系】"?
- [ ] KP 主判据是否只用 cusp sub_lord signify 分析，未混入 Parashari 判据？
- [ ] KP 结论是否与 Parashari 结论并列输出（禁）—— 应二选一？
- [ ] 时间窗是否用 Vimshottari sub-lord 段 + Moon 换 sub 触发日，不用 Tajika applying？
- [ ] Rahu/Ketu 处理是否按 "conjunct 优先、sign_lord 次之"？
- [ ] 用户是否明确切换到 KP 而非误开？

---

## 7. 技术 caveat

- **Ayanamsa 差异**：本 skill 用 True Citra，与 KP 原生 KP ayanamsa 差异 <1°，在 sub_lord 边界处偶有归属摇摆(边界±5' 内的 cusp)——判读时若 sub_lord 处 sub 边界(offset<0.5° in nak) 请手工核对。
- **House system**：本层用 Placidus 是 KP 传统；与主盘 whole-sign house 结果**不同**，这是 KP 独立性的一部分，不算 bug。
- **未实现**：Ruling Planets(RP) 是 KP 提问时刻的"当权星"筛选层，属高阶补充，未来可加进本 policy。
