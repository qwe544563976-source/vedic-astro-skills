#!/usr/bin/env python3
"""calc_optional_kp.py — Prashna KP (Krishnamurti Paddhati) 独立判读栈(沙箱内, C 类)

KP = Krishnamurti 创立的独立占星体系，判据用 sub-lord signify 判事件成败。
与 Parashari 判读**互斥**——启用 KP 后判读走 KP-only 栈，不与 Parashari 主结论叠加。

本模块物理隔离在 vedic-prashna 沙箱内，**绝不进共享 engine**。

沙箱化硬约束(vedic-prashna/SKILL.md §沙箱化硬约束):
- 只存在于 vedic-prashna/scripts/。
- **仅在用户显式开启 --enable-kp 时**追加输出到 structured_prashna.md。
- 判读时走 KP-only；Parashari 主判读段虽仍在 md 里但判读时忽略。

技术选型:
- House system: Placidus (KP 传统，与 Parashari whole-sign 不同——本层独立不打架)
- Ayanamsa:    True Citrapaksha(与主盘一致；KP 大师原用 KP ayanamsa 差异<1°，接受)
- Sub-lord:    Vimshottari 比例分割 Nakshatra(9 sub 每 Nakshatra)

对应 SKILL.md §可选沙箱层 · KP 独立判读栈。
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

# import engine 会触发 set_sid_mode(SIDM_TRUE_CITRA)，与主盘一致
from engine import (                              # noqa: E402
    to_jd, SIGNS, NAKSHATRAS, DASHA_ORDER, DASHA_YEARS,
)
import swisseph as swe                            # noqa: E402


NAK_SPAN = 360.0 / 27  # 13°20'
TOTAL_YEARS = sum(DASHA_YEARS.values())  # 120

SIGN_LORDS_KP = {
    'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury', 'Cancer': 'Moon',
    'Leo': 'Sun', 'Virgo': 'Mercury', 'Libra': 'Venus', 'Scorpio': 'Mars',
    'Sagittarius': 'Jupiter', 'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter',
}


def _sign_of(lon):
    return SIGNS[int(lon / 30) % 12]


def _sign_lord(lon):
    return SIGN_LORDS_KP[_sign_of(lon)]


def _star_lord(lon):
    """Nakshatra 主(与 Parashari 相同的 Nakshatra 分割)。"""
    return NAKSHATRAS[int((lon % 360) / NAK_SPAN)][1]


def _sub_lord(lon):
    """KP sub-lord: Nakshatra 主开始，Vimshottari 顺序按年数比例分 9 sub。"""
    lon = lon % 360
    nak_idx = int(lon / NAK_SPAN)
    nak_lord = NAKSHATRAS[nak_idx][1]
    offset_in_nak = lon - nak_idx * NAK_SPAN
    start_idx = DASHA_ORDER.index(nak_lord)
    cumulative = 0.0
    for i in range(9):
        lord = DASHA_ORDER[(start_idx + i) % 9]
        span = NAK_SPAN * DASHA_YEARS[lord] / TOTAL_YEARS
        if offset_in_nak < cumulative + span - 1e-9:
            return lord
        cumulative += span
    return DASHA_ORDER[(start_idx + 8) % 9]


def _fmt_deg_in_sign(lon):
    d = lon % 30
    di = int(d)
    mi = int((d - di) * 60)
    return f"{di}°{mi:02d}'"


def compute(dt_local, lat, lon_place, tz_str):
    """计算 Placidus cusps + 12 cusp KP 三主 + 10 planets(含 Lagna/Rahu/Ketu) KP 三主。"""
    jd = to_jd(dt_local.year, dt_local.month, dt_local.day,
               dt_local.hour, dt_local.minute, tz_str)
    flags = swe.FLG_SIDEREAL

    # Placidus cusps: swe.houses_ex 返回 (cusps[13], ascmc[10])
    # 注意 KP 传统用 sidereal Placidus；houses_ex 在 SIDM 已设时自动用 sidereal
    cusps, ascmc = swe.houses_ex(jd, lat, lon_place, b'P', flags)

    house_cusps = []
    for h in range(1, 13):
        c = cusps[h] % 360
        house_cusps.append({
            'house': h,
            'cusp_lon': round(c, 3),
            'sign': _sign_of(c),
            'deg_in_sign': _fmt_deg_in_sign(c),
            'sign_lord': _sign_lord(c),
            'star_lord': _star_lord(c),
            'sub_lord': _sub_lord(c),
        })

    # 行星: Lagna + Sun..Saturn + Rahu(Mean Node) + Ketu(Rahu+180)
    planet_ids = {
        'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS,
        'Mercury': swe.MERCURY, 'Jupiter': swe.JUPITER, 'Venus': swe.VENUS,
        'Saturn': swe.SATURN,
    }
    speed_flags = swe.FLG_SIDEREAL | swe.FLG_SPEED

    planet_kp = []
    lagna_lon = ascmc[0] % 360
    planet_kp.append({
        'name': 'Lagna', 'lon': round(lagna_lon, 3),
        'sign': _sign_of(lagna_lon), 'deg_in_sign': _fmt_deg_in_sign(lagna_lon),
        'sign_lord': _sign_lord(lagna_lon),
        'star_lord': _star_lord(lagna_lon),
        'sub_lord': _sub_lord(lagna_lon),
    })
    for name, pid in planet_ids.items():
        pos = swe.calc_ut(jd, pid, speed_flags)[0][0] % 360
        planet_kp.append({
            'name': name, 'lon': round(pos, 3),
            'sign': _sign_of(pos), 'deg_in_sign': _fmt_deg_in_sign(pos),
            'sign_lord': _sign_lord(pos),
            'star_lord': _star_lord(pos),
            'sub_lord': _sub_lord(pos),
        })
    rahu_lon = swe.calc_ut(jd, swe.MEAN_NODE, speed_flags)[0][0] % 360
    ketu_lon = (rahu_lon + 180) % 360
    for name, pos in [('Rahu', rahu_lon), ('Ketu', ketu_lon)]:
        planet_kp.append({
            'name': name, 'lon': round(pos, 3),
            'sign': _sign_of(pos), 'deg_in_sign': _fmt_deg_in_sign(pos),
            'sign_lord': _sign_lord(pos),
            'star_lord': _star_lord(pos),
            'sub_lord': _sub_lord(pos),
        })

    return {
        'ayanamsa_note': 'True Citrapaksha (与主盘一致；KP 原用 KP ayanamsa 差异<1°)',
        'house_system': 'Placidus (KP 传统)',
        'house_cusps': house_cusps,
        'planets_kp': planet_kp,
    }


def format_kp_section(data):
    lines = []
    lines.append("## KP 独立判读栈（用户主动切换）\n")
    lines.append("> ⚠️ **本段仅在用户显式开启 `--enable-kp` 时生成**。")
    lines.append("> KP (Krishnamurti Paddhati) = 独立判读体系，用 sub-lord signify 判事件成败。")
    lines.append("> **与 Parashari 主判读互斥、独立切换、不叠加、不同时作主结论**。")
    lines.append("> 用户开 KP = 承认走 KP 判读栈；Parashari 主判读段虽仍在 md 里，**判读时忽略**。\n")

    lines.append("### 判据配置\n")
    lines.append("```")
    lines.append(f"House system: {data['house_system']}")
    lines.append(f"Ayanamsa:     {data['ayanamsa_note']}")
    lines.append("Sub-lord 分割: Vimshottari 比例(9 sub 每 Nakshatra)")
    lines.append("参与行星: Lagna + Sun/Moon/Mars/Mercury/Jupiter/Venus/Saturn + Rahu/Ketu(Mean Node)")
    lines.append("```\n")

    lines.append("### 12 宫 Placidus Cusp · KP 三主\n")
    lines.append("| 宫 | Cusp | Sign | Sign lord | Star lord | **Sub lord** |")
    lines.append("|---|---|---|---|---|---|")
    for c in data['house_cusps']:
        lines.append(
            f"| {c['house']} | {c['deg_in_sign']} | {c['sign']} | "
            f"{c['sign_lord']} | {c['star_lord']} | **{c['sub_lord']}** |"
        )
    lines.append("")

    lines.append("### 行星 KP 三主\n")
    lines.append("| 行星 | 位置 | Sign | Sign lord | Star lord | **Sub lord** |")
    lines.append("|---|---|---|---|---|---|")
    for p in data['planets_kp']:
        lines.append(
            f"| {p['name']} | {p['deg_in_sign']} | {p['sign']} | "
            f"{p['sign_lord']} | {p['star_lord']} | **{p['sub_lord']}** |"
        )
    lines.append("")

    lines.append("### 判读消费入口\n")
    lines.append("详细语义映射见 `resources/kp-optional.md`。")
    lines.append('**判读单里切换到 KP 判读栈时，必须显式标注"【KP 判读栈·独立体系】"，且不与 Parashari 结论叠加**。\n')
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Prashna KP 独立判读栈 CLI")
    ap.add_argument("--datetime", required=True, help='"YYYY-MM-DD HH:MM" 或 "now"')
    ap.add_argument("--lat", type=float, required=True)
    ap.add_argument("--lon", type=float, required=True)
    ap.add_argument("--tz", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    dt = datetime.now() if args.datetime.strip().lower() == "now" \
        else datetime.strptime(args.datetime, "%Y-%m-%d %H:%M")

    data = compute(dt, args.lat, args.lon, args.tz)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(format_kp_section(data))


if __name__ == "__main__":
    main()
