#!/usr/bin/env python3
"""calc_optional_tajika.py — Prashna Tajika 副层计算(沙箱内，B 类可选启用)

Tajika = 波斯-印度年运体系(Al-Biruni 传入印度化千年，Varshaphala/年运即用它)。
判据基于 orb applying/separating aspect —— 与主体系(Parashari 整宫落点+Graha Drishti)
**口径不同**。因此本模块被物理隔离在 vedic-prashna 沙箱内，**绝不进共享 engine**。

沙箱化硬约束(vedic-prashna/SKILL.md §沙箱化硬约束):
- 本脚本只存在于 vedic-prashna/scripts/。
- Tajika 输出**仅在用户显式开启 --enable-tajika 时**追加到 structured_prashna.md。
- Tajika 结论**独立并行于 Parashari 主判读、不叠加主结论**；判读冲突时以 Parashari 为准。

实现 4 种主要 Tajika 判据：
- Ithasala   — 快星向慢星 applying aspect(事在应)
- Ishraga    — 快星已过 exact aspect，separating(事已过)
- Muthashila — 0° applying 合相(事将紧密结合)
- Manau      — 光传递: Moon → 中间星 Y → 目标星 X(间接接触)

未实现（流派差异大，先跳过）：Kambula 特殊组合。
Rahu/Ketu 不参与(KN Rao 主线口径)。
Retro 时该对跳过(Retro 变向使 applying/separating 判定不稳)。

对应 SKILL.md §可选沙箱层 · Tajika 副层。
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_CALC = _HERE.parent.parent / "vedic-calculator" / "scripts"
if str(_CALC) not in sys.path:
    sys.path.insert(0, str(_CALC))

from engine import calculate_full_chart  # noqa: E402


# --- Tajika 参数(经典配置，KN Rao 主线口径) ---
TAJIKA_PLANETS = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
TAJIKA_ORBS = {
    'Sun': 15, 'Moon': 12, 'Mars': 8, 'Mercury': 7,
    'Jupiter': 9, 'Venus': 7, 'Saturn': 9,
}
TAJIKA_ASPECTS = [
    (0,   '合(conj)'),
    (60,  '六合(sextile)'),
    (90,  '刑(square)'),
    (120, '三合(trine)'),
    (180, '冲(opposition)'),
]


def _aspect_offset(fast_lon, slow_lon, aspect_angle):
    """快星相对慢星在 aspect_angle 位置的**有符号偏差**，归一化到 [-180, 180)。
    offset < 0: 快星未到 exact aspect(applying)
    offset > 0: 快星已过 exact aspect(separating)
    """
    return ((fast_lon - slow_lon - aspect_angle + 180) % 360) - 180


def compute(chart):
    """返回 dict {ithasala, ishraga, muthashila, manau, skipped_retro, config}。"""
    planets = chart['planets']
    results = {
        'ithasala': [], 'ishraga': [], 'muthashila': [],
        'manau': [], 'skipped_retro': [],
    }

    # 两两配对(仅 TAJIKA_PLANETS)
    P = [p for p in TAJIKA_PLANETS if p in planets]
    pair_contacts = {}  # (a, b) → aspect record if in orb

    for i, a in enumerate(P):
        for b in P[i + 1:]:
            pa, pb = planets[a], planets[b]
            sa, sb = pa.get('speed', 0), pb.get('speed', 0)

            if sa <= 0 or sb <= 0:
                results['skipped_retro'].append({
                    'pair': f"{a}–{b}",
                    'reason': f"Retro 涉及({a}={sa:.3f}, {b}={sb:.3f}) — Tajika 判定不稳"
                })
                continue

            # 确定快/慢星
            if abs(sa) >= abs(sb):
                fast, slow = a, b
                fp, sp = pa, pb
            else:
                fast, slow = b, a
                fp, sp = pb, pa

            orb_sum = (TAJIKA_ORBS[fast] + TAJIKA_ORBS[slow]) / 2.0

            matched = None
            for angle, label in TAJIKA_ASPECTS:
                offset = _aspect_offset(fp['longitude'], sp['longitude'], angle)
                if abs(offset) <= orb_sum:
                    matched = (angle, label, offset, orb_sum)
                    break

            if not matched:
                continue

            angle, label, offset, orb_sum = matched
            record = {
                'fast': fast, 'slow': slow,
                'aspect_angle': angle, 'aspect_label': label,
                'offset_deg': round(offset, 3),
                'orb_sum': round(orb_sum, 2),
                'fast_lon': round(fp['longitude'], 3),
                'slow_lon': round(sp['longitude'], 3),
                'fast_sign': fp['sign'], 'slow_sign': sp['sign'],
                'fast_speed': round(sa if fast == a else sb, 3),
            }
            pair_contacts[(a, b)] = (angle, offset)

            if angle == 0 and offset < 0:
                results['muthashila'].append(record)
            elif offset < 0:
                results['ithasala'].append(record)
            else:  # offset >= 0
                results['ishraga'].append(record)

    # Manau: Moon → Y → X 光传递(Moon Ithasala Y AND Y Ithasala/Muthashila X, Y 非 Moon 非 X)
    def in_ithasala_or_muthashila(p1, p2):
        """检查 p1 和 p2 是不是 Ithasala 或 Muthashila 关系(任一顺序)。"""
        for rec in results['ithasala'] + results['muthashila']:
            if {rec['fast'], rec['slow']} == {p1, p2}:
                return rec
        return None

    if 'Moon' in planets:
        for X in TAJIKA_PLANETS:
            if X == 'Moon':
                continue
            # Moon 与 X 有直接 Ithasala/Muthashila 就不需要 Manau
            if in_ithasala_or_muthashila('Moon', X):
                continue
            for Y in TAJIKA_PLANETS:
                if Y in ('Moon', X):
                    continue
                if in_ithasala_or_muthashila('Moon', Y) and in_ithasala_or_muthashila(Y, X):
                    results['manau'].append({
                        'from': 'Moon', 'via': Y, 'to': X,
                        'note': f"Moon 通过 {Y} 传光到 {X}(间接接触)"
                    })

    results['config'] = {
        'planets': TAJIKA_PLANETS,
        'aspects_deg': [a for a, _ in TAJIKA_ASPECTS],
        'orbs': TAJIKA_ORBS,
        'excluded': ['Rahu', 'Ketu'],
        'retro_policy': 'skip_pair',
    }
    return results


def format_tajika_section(data):
    lines = []
    lines.append("## Tajika 补充参考（orb 制副层 · 用户主动启用）\n")
    lines.append("> ⚠️ **本段仅在用户显式开启 `--enable-tajika` 时生成**。")
    lines.append("> Tajika = 波斯-印度年运体系(Varshaphala)，用 orb 制 applying/separating aspect。")
    lines.append("> **与 Parashari 主判读独立并行、不叠加主结论**，仅作 orb 层参考补充。")
    lines.append("> Tajika 与主体系(整宫落点 + Graha Drishti)口径不同。")
    lines.append("> **冲突时以 Parashari 主结论为准。**\n")

    cfg = data['config']
    lines.append("### 判据配置\n")
    lines.append("```")
    lines.append(f"参与行星: {' / '.join(cfg['planets'])}（Rahu/Ketu 主线不参与）")
    lines.append(f"Aspect angles: {' / '.join(str(a)+'°' for a in cfg['aspects_deg'])}")
    lines.append("Orb 表: " + ", ".join(f"{p} {v}°" for p, v in cfg['orbs'].items()))
    lines.append("两星 orb sum = (orb_A + orb_B) / 2")
    lines.append("Retro 参与的对 → 跳过(applying/separating 判定不稳)")
    lines.append("```\n")

    # Ithasala
    lines.append("### Ithasala（Applying aspect · 事在应）\n")
    if data['ithasala']:
        lines.append("| 快–慢 | Aspect | 偏差 | Orb sum |")
        lines.append("|---|---|---|---|")
        for r in data['ithasala']:
            lines.append(
                f"| {r['fast']}–{r['slow']} | {r['aspect_label']} "
                f"({r['aspect_angle']}°) | {r['offset_deg']}° "
                f"(距 exact {abs(r['offset_deg'])}°) | ±{r['orb_sum']}° |"
            )
    else:
        lines.append("- 无\n")
    lines.append("")

    # Ishraga
    lines.append("### Ishraga（Separating aspect · 事已过）\n")
    if data['ishraga']:
        lines.append("| 快–慢 | Aspect | 偏差 | Orb sum |")
        lines.append("|---|---|---|---|")
        for r in data['ishraga']:
            lines.append(
                f"| {r['fast']}–{r['slow']} | {r['aspect_label']} "
                f"({r['aspect_angle']}°) | +{r['offset_deg']}° | ±{r['orb_sum']}° |"
            )
    else:
        lines.append("- 无\n")
    lines.append("")

    # Muthashila
    lines.append("### Muthashila（Applying 合相 · 事将紧密结合）\n")
    if data['muthashila']:
        lines.append("| 快–慢 | 偏差 | Orb sum |")
        lines.append("|---|---|---|")
        for r in data['muthashila']:
            lines.append(f"| {r['fast']}–{r['slow']} | {r['offset_deg']}° | ±{r['orb_sum']}° |")
    else:
        lines.append("- 无\n")
    lines.append("")

    # Manau
    lines.append("### Manau（光传递 · Moon → 中间星 → 目标）\n")
    if data['manau']:
        for m in data['manau']:
            lines.append(f"- **Moon → {m['via']} → {m['to']}**: {m['note']}")
    else:
        lines.append("- 无")
    lines.append("")

    # Skipped
    if data['skipped_retro']:
        lines.append("### 跳过的对（Retro 涉及）\n")
        for s in data['skipped_retro']:
            lines.append(f"- {s['pair']}: {s['reason']}")
        lines.append("")

    lines.append("### 判读消费入口\n")
    lines.append("详细语义映射见 `resources/tajika-optional.md`。")
    lines.append('**判读单里若引用本段，必须显式标注"【Tajika 补充参考·orb 制】"，且不作主结论**。\n')

    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Prashna Tajika 副层独立 CLI")
    ap.add_argument("--datetime", required=True, help='"YYYY-MM-DD HH:MM" 或 "now"')
    ap.add_argument("--lat", type=float, required=True)
    ap.add_argument("--lon", type=float, required=True)
    ap.add_argument("--tz", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    dt = datetime.now() if args.datetime.strip().lower() == "now" \
        else datetime.strptime(args.datetime, "%Y-%m-%d %H:%M")

    chart = calculate_full_chart(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                                 args.lat, args.lon, args.tz)
    data = compute(chart)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(format_tajika_section(data))


if __name__ == "__main__":
    main()
