#!/usr/bin/env python3
"""calc_moon_vedic.py — Prashna Moon 吠陀动向计算(沙箱内)

计算 SKILL.md 主判读 Step 3 需要的两块字段(纯吠陀口径，无 orb)：
- chandra_kriya: Moon 空亡判定(整宫落点 + Graha Drishti 触及，禁 VoC 西占口径)
- moon_next_contact: Moon 换 Nakshatra + 换 Sign 时刻 + 换后接触集合

沙箱化硬约束(vedic-prashna/SKILL.md §沙箱化硬约束):
- 本脚本只存在于 vedic-prashna/scripts/，绝不下沉共享 vedic-calculator/scripts/engine.py。
- 只读复用共享 engine 的 to_jd/get_house/get_nakshatra/SIGNS/NAKSHATRAS/calc_planet 等基础工具。
- 输出仅由 build_prashna_data.py 追加到 prashna_*/structured_prashna.md。

对应 SKILL.md §主判读方法论 · Step 3 消费入口。
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# --- 复用共享 vedic-calculator(只读) ---
_HERE = Path(__file__).resolve().parent            # vedic-prashna/scripts/
_CALC = _HERE.parent.parent / "vedic-calculator" / "scripts"
if str(_CALC) not in sys.path:
    sys.path.insert(0, str(_CALC))

# 导入 engine 会顺带 set_sid_mode(SIDM_TRUE_CITRA)，与主排盘一致
from engine import (                                # noqa: E402
    calculate_full_chart, to_jd, get_house, SIGNS, NAKSHATRAS,
)
import swisseph as swe                              # noqa: E402
import pytz                                         # noqa: E402


# Prashna Moon 判读用 SPECIAL_DRISHTI(承 engine.calc_graha_drishti 口径)
SPECIAL_DRISHTI = {'Mars': [4, 8], 'Jupiter': [5, 9], 'Saturn': [3, 10]}
DRISHTI_PLANETS = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus',
                   'Saturn', 'Rahu', 'Ketu']
NAK_SPAN = 360.0 / 27       # 13°20'
MOON_AVG_DEG_PER_DAY = 13.176  # 只作 fallback 估算，精确时刻由 swisseph 二分


# ---------------------------------------------------------------------------
# 接触判定(整宫落点 + Graha Drishti，禁 orb)
# ---------------------------------------------------------------------------
def _planets_aspecting_sign(planets, lagna_sign_idx, target_sign_idx):
    """哪些行星通过 graha drishti 触及 target sign(不含 Moon 本身、不含合宫)。"""
    target_house = get_house(target_sign_idx, lagna_sign_idx)
    hits = []
    for name in DRISHTI_PLANETS:
        p = planets.get(name)
        if not p or name == 'Moon':
            continue
        src_house = p['house']
        angles = [7] + SPECIAL_DRISHTI.get(name, [])
        for a in angles:
            if ((src_house - 1 + (a - 1)) % 12) + 1 == target_house:
                hits.append({
                    'planet': name, 'from_sign': p['sign'],
                    'from_house': src_house, 'aspect_angle': a,
                })
                break
    return hits


def _planets_colocated_with(planets, target_sign_idx):
    """与 target sign 合宫的行星(不含 Moon 本身)。"""
    hits = []
    for name in DRISHTI_PLANETS:
        p = planets.get(name)
        if not p or name == 'Moon':
            continue
        if p['sign_idx'] == target_sign_idx:
            hits.append({'planet': name, 'sign': p['sign'], 'house': p['house']})
    return hits


# ---------------------------------------------------------------------------
# Moon 边界时刻求解(swisseph 二分，True Citra sidereal)
# ---------------------------------------------------------------------------
def _find_moon_boundary_jd(start_jd, start_lon, target_lon, tol=1e-4):
    """从 start_jd 找 Moon 第一次到达 target_lon 的 jd(sidereal True Citra)。

    Moon 周期 ~27.3 天，二分不能用"当前 lon 相对 target 差"判定(会跳到下一圈)——
    改用"从 start_lon 起已走过角度 vs 到 target 的前进角距"判定，保证收敛到本圈。
    """
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
    delta_deg = (target_lon - start_lon) % 360
    if delta_deg < 0.001:
        # Moon 已在边界或刚过，找下一次到达
        delta_deg += 360
    t_est_days = delta_deg / MOON_AVG_DEG_PER_DAY
    lo = start_jd
    hi = start_jd + t_est_days + 0.5  # 略大于估算，确保 hi 已过 target 但未跨下一圈
    for _ in range(60):
        mid = (lo + hi) / 2
        pos = swe.calc_ut(mid, swe.MOON, flags)[0][0]
        walked = (pos - start_lon) % 360
        # 若 walked 明显小(< 30°)但估算的 delta_deg 很大，说明 Moon 已跨圈——保护带
        if walked >= delta_deg or (walked < 30 and delta_deg > 300):
            hi = mid
        else:
            lo = mid
        if hi - lo < tol:
            break
    return (lo + hi) / 2


def _jd_to_local_dt(jd, tz_str):
    y, m, d, h_frac = swe.revjul(jd)
    hh = int(h_frac)
    mm_frac = (h_frac - hh) * 60
    mm = int(mm_frac)
    ss = int((mm_frac - mm) * 60)
    utc_dt = datetime(int(y), int(m), int(d), hh, mm, ss, tzinfo=pytz.utc)
    return utc_dt.astimezone(pytz.timezone(tz_str))


# ---------------------------------------------------------------------------
# 核心 compute
# ---------------------------------------------------------------------------
def compute(chart, dt_local, tz_str):
    """给定 chart(engine 返回) + 提问 datetime + tz，输出 chandra_kriya + moon_next_contact。"""
    moon = chart['planets']['Moon']
    planets = chart['planets']
    lagna_sign_idx = chart['lagna']['sign_idx']
    moon_sign_idx = moon['sign_idx']
    moon_degree = moon['degree']
    moon_house = moon['house']
    moon_nak = moon['nakshatra']
    moon_lon = moon['longitude']

    # ---- chandra_kriya: 当前状态 + 空亡判定 ----
    conj = _planets_colocated_with(planets, moon_sign_idx)
    aspecting = _planets_aspecting_sign(planets, lagna_sign_idx, moon_sign_idx)
    is_void = len(conj) == 0 and len(aspecting) == 0

    remain_in_sign_deg = 30.0 - moon_degree
    nak_start = (int(moon_lon / NAK_SPAN)) * NAK_SPAN
    remain_in_nak_deg = NAK_SPAN - (moon_lon - nak_start)

    chandra_kriya = {
        'moon_sign': moon['sign'],
        'moon_nakshatra': moon_nak['name'],
        'moon_pada': moon_nak['pada'],
        'moon_nak_lord': moon_nak['lord'],
        'moon_house': moon_house,
        'remaining_in_nakshatra_deg': round(remain_in_nak_deg, 3),
        'remaining_in_nakshatra_days_approx': round(remain_in_nak_deg / MOON_AVG_DEG_PER_DAY, 2),
        'remaining_in_sign_deg': round(remain_in_sign_deg, 3),
        'remaining_in_sign_days_approx': round(remain_in_sign_deg / MOON_AVG_DEG_PER_DAY, 2),
        'conjunctions': conj,
        'aspecting_planets': [h['planet'] for h in aspecting],
        'aspecting_details': aspecting,
        'is_void': is_void,
        'void_note': (
            "Moon 在当前 sign 内无任何整宫合宫或 Graha Drishti 触及 = 空亡 = "
            "Prashna Marga 拒绝式判据触发(见 judgment-rubric.md §3 拒绝式 #1)"
        ) if is_void else None,
    }

    # ---- moon_next_contact: 换 Nakshatra + 换 Sign 时刻 + 换后接触集合 ----
    start_jd = to_jd(dt_local.year, dt_local.month, dt_local.day,
                     dt_local.hour, dt_local.minute, tz_str)

    target_nak_lon = (nak_start + NAK_SPAN) % 360
    jd_next_nak = _find_moon_boundary_jd(start_jd, moon_lon, target_nak_lon)
    dt_next_nak = _jd_to_local_dt(jd_next_nak, tz_str)
    next_nak_idx = int(target_nak_lon / NAK_SPAN) % 27
    next_nak_name, next_nak_lord = NAKSHATRAS[next_nak_idx]

    target_sign_lon = ((int(moon_lon / 30) + 1) * 30) % 360
    jd_next_sign = _find_moon_boundary_jd(start_jd, moon_lon, target_sign_lon)
    dt_next_sign = _jd_to_local_dt(jd_next_sign, tz_str)
    next_sign_idx = int(target_sign_lon / 30) % 12
    next_sign_house = get_house(next_sign_idx, lagna_sign_idx)

    # 换 sign 后的新接触集合(几天内其他行星移动忽略，用 chart 当前位置近似)
    new_conj = _planets_colocated_with(planets, next_sign_idx)
    new_aspecting = _planets_aspecting_sign(planets, lagna_sign_idx, next_sign_idx)

    moon_next_contact = {
        'next_nakshatra_switch': {
            'datetime': dt_next_nak.strftime('%Y-%m-%d %H:%M %Z'),
            'days_from_query': round(jd_next_nak - start_jd, 3),
            'new_nakshatra': next_nak_name,
            'new_pada': 1,
            'new_nak_lord': next_nak_lord,
            'note': "换 Nakshatra 对应 Vimshottari Dasha 段转，是主要择时触发日之一。"
        },
        'next_sign_switch': {
            'datetime': dt_next_sign.strftime('%Y-%m-%d %H:%M %Z'),
            'days_from_query': round(jd_next_sign - start_jd, 3),
            'new_sign': SIGNS[next_sign_idx],
            'new_house': next_sign_house,
            'new_conjunctions': new_conj,
            'new_aspecting_planets': [h['planet'] for h in new_aspecting],
            'new_aspecting_details': new_aspecting,
            'note': "换 sign 后 Moon 所在宫更新→接触集合更新；判'心念下一步指向哪'。"
        },
    }

    return {
        'chandra_kriya': chandra_kriya,
        'moon_next_contact': moon_next_contact,
    }


# ---------------------------------------------------------------------------
# 格式化为 markdown 段(供 build_prashna_data.py 追加到 structured_prashna.md)
# ---------------------------------------------------------------------------
def format_moon_section(moon_data):
    ck = moon_data['chandra_kriya']
    nc = moon_data['moon_next_contact']
    lines = []

    lines.append("## Moon 吠陀动向（Prashna 判读 Step 3 输入）\n")

    lines.append("### Chandra Kriya（Moon 空亡吠陀口径）\n")
    lines.append("```")
    lines.append(f"Moon 当前: {ck['moon_sign']} · {ck['moon_nakshatra']}(pada {ck['moon_pada']}) · 宫 {ck['moon_house']}")
    lines.append(f"Nakshatra 主: {ck['moon_nak_lord']}  (对应 Vimshottari 段主)")
    lines.append(f"Moon 剩余在当前 Nakshatra: {ck['remaining_in_nakshatra_deg']}°  (~{ck['remaining_in_nakshatra_days_approx']} 天)")
    lines.append(f"Moon 剩余在当前 Sign:      {ck['remaining_in_sign_deg']}°  (~{ck['remaining_in_sign_days_approx']} 天)")
    lines.append("```\n")

    lines.append("**当前接触集合**（吠陀口径：整宫合宫 + Graha Drishti 触及，无 orb）\n")
    if ck['conjunctions']:
        for c in ck['conjunctions']:
            lines.append(f"- 合宫: **{c['planet']}** (同 sign, 宫 {c['house']})")
    else:
        lines.append("- 合宫: 无")
    if ck['aspecting_details']:
        for a in ck['aspecting_details']:
            lines.append(f"- Graha Drishti: **{a['planet']}** (from 宫 {a['from_house']}, {a['aspect_angle']}th 相位)")
    else:
        lines.append("- Graha Drishti 触及: 无")
    lines.append("")

    void_mark = ("✗ **Void（空亡=拒绝式判据触发）**"
                 if ck['is_void'] else
                 "✓ 非 Void（有 significator 接触，事有载体）")
    lines.append(f"**Void 判定**: {void_mark}\n")
    if ck['is_void'] and ck['void_note']:
        lines.append(f"> {ck['void_note']}\n")

    lines.append("### Moon 下一次接触（moon_next_contact）\n")
    nn = nc['next_nakshatra_switch']
    lines.append("**Moon 换 Nakshatra**\n")
    lines.append("```")
    lines.append(f"时刻: {nn['datetime']}  ({nn['days_from_query']} 天后)")
    lines.append(f"新 Nakshatra: {nn['new_nakshatra']} · pada 1 · 主 {nn['new_nak_lord']}")
    lines.append("```")
    lines.append(f"> {nn['note']}\n")

    ns = nc['next_sign_switch']
    lines.append("**Moon 换 Sign**\n")
    lines.append("```")
    lines.append(f"时刻: {ns['datetime']}  ({ns['days_from_query']} 天后)")
    lines.append(f"新 Sign: {ns['new_sign']}  (Lagna 视角新宫 {ns['new_house']})")
    lines.append("新接触集合:")
    if ns['new_conjunctions']:
        for c in ns['new_conjunctions']:
            lines.append(f"  - 合宫: {c['planet']} (宫 {c['house']})")
    else:
        lines.append("  - 合宫: 无")
    if ns['new_aspecting_details']:
        for a in ns['new_aspecting_details']:
            lines.append(f"  - Graha Drishti: {a['planet']} (from 宫 {a['from_house']}, {a['aspect_angle']}th)")
    else:
        lines.append("  - Graha Drishti 触及: 无")
    lines.append("```")
    lines.append(f"> {ns['note']}\n")

    lines.append("### 判读时消费入口\n")
    lines.append("详细语义映射见 `resources/moon-policy.md`。SKILL.md 主判读 Step 3 引用本段字段。\n")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI(独立 demo，可用于快速核对某个提问盘的 Moon 动向)
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Prashna Moon 吠陀动向独立 CLI")
    ap.add_argument("--datetime", required=True, help='"YYYY-MM-DD HH:MM" 或 "now"')
    ap.add_argument("--lat", type=float, required=True)
    ap.add_argument("--lon", type=float, required=True)
    ap.add_argument("--tz", required=True)
    ap.add_argument("--json", action="store_true", help="输出 JSON 而非 markdown")
    args = ap.parse_args()

    dt = datetime.now() if args.datetime.strip().lower() == "now" \
        else datetime.strptime(args.datetime, "%Y-%m-%d %H:%M")

    chart = calculate_full_chart(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                                 args.lat, args.lon, args.tz)
    data = compute(chart, dt, args.tz)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(format_moon_section(data))


if __name__ == "__main__":
    main()
