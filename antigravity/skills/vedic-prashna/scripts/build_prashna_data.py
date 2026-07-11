#!/usr/bin/env python3
"""build_prashna_data.py — Prashna 提问盘起盘链路

调共享 vedic-calculator/scripts/engine.py 的 calculate_full_chart(提问时刻)，
组装 structured_prashna.md 写入 prashna_<yyyymmdd_HHMM>_<label>/ 独立目录。

沙箱化硬约束(vedic-prashna/SKILL.md §沙箱化硬约束):
  1. 复用共享 engine/formatter，只读调用，不改任何共享代码。
  2. 产物名 structured_prashna.md(与本命 structured_data.md 严格区分)。
  3. 产物路径 prashna_<yyyymmdd_HHMM>_<label>/(独立子目录，不写本命根)。
  4. 不加任何 Tajika/KP/异体系字段。

Prashna 语义微调:
  - 过运段(transit) 传 None 跳过——共享 calc_transit 用"当前时刻"计算，
    与"提问时刻"语义不符；Prashna 判读栈以 Dasha + graha drishti + Karaka + SAV 为主，
    不吃过运。
  - 元信息头段/用户信息头段重写为 Prashna 口径(提问日期/提问信息)；
    D1 及后续数据段复用共享 formatter 输出。

用法:
    python build_prashna_data.py \\
        --datetime "2026-07-11 15:30"  # 提问时刻(本地时区)，或 "now" \\
        --lat 30.667 --lon 104.067      # 提问地(度，正=北/东) \\
        --tz "Asia/Shanghai"            # 提问地时区 \\
        --question "这份 offer 该不该接?" \\
        --label offer-decide            # 问题短标签(a-z0-9-, 1-30) \\
        [--out-parent .]                # 独立子目录的父目录(默认 CWD)
"""
import argparse
import re
import sys
from datetime import datetime
from pathlib import Path


# --- 复用共享 vedic-calculator(只读调用) ---
_HERE = Path(__file__).resolve().parent           # vedic-prashna/scripts/
_CALC_SCRIPTS = _HERE.parent.parent / "vedic-calculator" / "scripts"
if not _CALC_SCRIPTS.exists():
    raise RuntimeError(
        f"[FATAL] 未找到共享 vedic-calculator/scripts: {_CALC_SCRIPTS}\n"
        f"沙箱化硬约束 #1 要求 Prashna 复用共享 engine，请检查 skills 目录布局。"
    )
if str(_CALC_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_CALC_SCRIPTS))

from engine import calculate_full_chart      # noqa: E402
from formatter import format_structured_data  # noqa: E402
from transit import calc_transit              # noqa: E402
import pytz                                   # noqa: E402

# 沙箱内 Moon 吠陀动向计算(不下沉 engine，见 calc_moon_vedic.py 顶注)
from calc_moon_vedic import compute as compute_moon_vedic  # noqa: E402
from calc_moon_vedic import format_moon_section            # noqa: E402

# Tajika 副层(B 类可选)：仅在 --enable-tajika 时使用
from calc_optional_tajika import compute as compute_tajika  # noqa: E402
from calc_optional_tajika import format_tajika_section     # noqa: E402

# KP 独立判读栈(C 类可选，独立体系)：仅在 --enable-kp 时使用
from calc_optional_kp import compute as compute_kp         # noqa: E402
from calc_optional_kp import format_kp_section             # noqa: E402


LABEL_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,29}$")
D1_ANCHOR = "## D1基础数据"


def parse_args():
    ap = argparse.ArgumentParser(description="Prashna 提问盘起盘")
    ap.add_argument("--datetime", required=True,
                    help='提问时刻，格式 "YYYY-MM-DD HH:MM"，或 "now"')
    ap.add_argument("--lat", type=float, required=True, help="提问地纬度(度，正=北)")
    ap.add_argument("--lon", type=float, required=True, help="提问地经度(度，正=东)")
    ap.add_argument("--tz", required=True, help='提问地时区，如 "Asia/Shanghai"')
    ap.add_argument("--question", required=True, help="具体问题(单一可判定)")
    ap.add_argument("--label", required=True,
                    help="问题短标签(kebab-case, 1-30 字符 [a-z0-9-])")
    ap.add_argument("--out-parent", default=".",
                    help="独立子目录的父目录(默认 CWD)")
    ap.add_argument("--enable-tajika", action="store_true",
                    help="启用 Tajika 副层(B 类可选，orb 制副层，默认关；见 tajika-optional.md)")
    ap.add_argument("--enable-kp", action="store_true",
                    help="切换到 KP 独立判读栈(C 类互斥体系，默认关；启用后判读走 KP-only)")
    args = ap.parse_args()

    if args.enable_tajika and args.enable_kp:
        ap.error("--enable-tajika 与 --enable-kp 互斥: "
                 "Tajika 是 Parashari 副层，KP 是独立体系；不能同时启用。"
                 "让用户二选一。")

    if not LABEL_RE.match(args.label):
        ap.error(f"--label 必须匹配 {LABEL_RE.pattern}: 收到 {args.label!r}")

    if args.datetime.strip().lower() == "now":
        dt = datetime.now()
    else:
        try:
            dt = datetime.strptime(args.datetime, "%Y-%m-%d %H:%M")
        except ValueError as e:
            ap.error(f"--datetime 格式应为 'YYYY-MM-DD HH:MM' 或 'now': {e}")

    args.dt = dt
    return args


def build_prashna_header(dt, lat, lon, tz, question, label,
                         chart_ayanamsa, dst_info, transit_note=None):
    lines = []
    lines.append("## 元信息\n")
    lines.append("```")
    lines.append("盘类型: Prashna(提问盘/时盘) — 独立生态位，不与本命混")
    lines.append(f"提问日期: {dt.strftime('%Y-%m-%d')}")
    lines.append(f"提问时间: {dt.strftime('%H:%M')}")
    lines.append(f"提问地点: ({lon:.3f}, {lat:.3f})")
    lines.append(f"时区: {tz}")
    lines.append("时间精度: 精确到分钟(用户报时或本机时刻)")
    lines.append("读盘方式: vedic-calculator 直接起 Prashna Kundali")
    lines.append(f"Ayanamsa: True Chitrapaksha(Lahiri 系) ({chart_ayanamsa:.4f}°)")
    if dst_info and dst_info.get('is_dst'):
        lines.append(
            f"夏令时: ⚠️ 提问时刻处于当地夏令时期间(UTC 偏移 {dst_info['utc_offset']})"
        )
    lines.append("Node模式: Mean Node")
    if transit_note:
        lines.append(f"过运语义: {transit_note}")
    lines.append("```\n")

    lines.append("## 提问信息\n")
    lines.append("```")
    lines.append(f"具体问题: {question}")
    lines.append(f"问题短标签: {label}")
    lines.append("求问者背景: [Prashna 分析阶段禁读盘主背景，此处留空]")
    lines.append("占卜类别: [由判读时依据 question 映射，见 resources/house-karaka-map.md]")
    lines.append("```\n")
    return "\n".join(lines)


def strip_header_before_d1(md):
    """从共享 formatter 输出中切掉本命头部(元信息+用户信息)，返回 D1 及之后所有段。

    切分锚点=D1_ANCHOR；若锚点未找到则报错——防共享 formatter 输出结构漂移导致
    Prashna 头部与本命头部并排出现。
    """
    idx = md.find(D1_ANCHOR)
    if idx < 0:
        raise RuntimeError(
            f"[FATAL] 共享 formatter 输出未包含分段锚点 {D1_ANCHOR!r}——"
            "vedic-calculator/scripts/formatter.py 的段落结构可能已变；"
            "请核对并同步 build_prashna_data.py 的锚点常量。"
        )
    return md[idx:]


def main():
    args = parse_args()

    # 1. 起盘(复用共享 engine，只读调用)
    chart = calculate_full_chart(
        args.dt.year, args.dt.month, args.dt.day,
        args.dt.hour, args.dt.minute,
        args.lat, args.lon, args.tz,
    )

    # 2. 判过运语义：当下起盘(dt ≈ now) → 调 calc_transit，两时刻一致语义正确；
    #    复盘旧提问(dt 与 now 相差 ≥24h) → 传 None，避免用"今日过运"填"过去提问时刻"
    now_local = datetime.now(pytz.timezone(args.tz)).replace(tzinfo=None)
    delta_hours = abs((args.dt - now_local).total_seconds()) / 3600.0
    if delta_hours < 24:
        transit_data = calc_transit(
            chart['lagna']['sign_idx'],
            chart['planets']['Moon']['sign_idx'],
            args.tz,
        )
        transit_note = f"当下起盘(提问时刻与当前差 {delta_hours:.1f}h) — 过运段数据有效"
    else:
        transit_data = None
        transit_note = (f"复盘旧提问(提问时刻距当前 {delta_hours:.0f}h ≥ 24h) — "
                        "过运段留空避免语义错位;时间窗判据以 Dasha + Moon Nakshatra 段转为主")

    # 3. 用 shim 值调 formatter 生成本命格式 md
    shim_meta = {
        'dob': args.dt.strftime('%Y-%m-%d'),
        'time': args.dt.strftime('%H:%M'),
        'place': f"(lon {args.lon:.3f}, lat {args.lat:.3f})",
        'lat': args.lat, 'lon': args.lon,
        'time_precision': '精确到分钟',
        'time_source': '提问',
        'effective_precision': '±分钟级',
    }
    shim_user_info = {'gender': '-', 'relationship': '-'}
    full_md = format_structured_data(chart, transit_data, shim_meta, shim_user_info)
    data_section = strip_header_before_d1(full_md)

    # 4. 组装 Prashna 专用头部(附带过运语义说明)
    head = build_prashna_header(
        args.dt, args.lat, args.lon, args.tz, args.question, args.label,
        chart['ayanamsa'], chart.get('dst_info'), transit_note,
    )

    # 5. Moon 吠陀动向(沙箱内计算，SKILL.md 主判读 Step 3 消费入口)
    moon_data = compute_moon_vedic(chart, args.dt, args.tz)
    moon_section = format_moon_section(moon_data)

    final_md = head + "\n" + data_section + "\n\n---\n\n" + moon_section

    # 4.5 Tajika 副层(B 类可选，仅在 --enable-tajika 时追加)
    if args.enable_tajika:
        tajika_data = compute_tajika(chart)
        final_md += "\n\n---\n\n" + format_tajika_section(tajika_data)

    # 4.6 KP 独立判读栈(C 类可选，仅在 --enable-kp 时追加；与 Tajika 互斥)
    if args.enable_kp:
        kp_data = compute_kp(args.dt, args.lat, args.lon, args.tz)
        final_md += "\n\n---\n\n" + format_kp_section(kp_data)

    # 5. 写入独立子目录(沙箱化硬约束 #3)
    subdir_name = f"prashna_{args.dt.strftime('%Y%m%d_%H%M')}_{args.label}"
    out_dir = Path(args.out_parent).resolve() / subdir_name
    out_dir.mkdir(parents=True, exist_ok=True)
    # 产物名严格区分本命根 structured_data.md
    out_path = out_dir / "structured_prashna.md"
    out_path.write_text(final_md, encoding='utf-8')

    print(f"[OK] Prashna 盘已生成:")
    print(f"     目录: {out_dir}")
    print(f"     文件: structured_prashna.md")
    print(f"     提问时刻: {args.dt.strftime('%Y-%m-%d %H:%M')} ({args.tz})")
    print(f"     具体问题: {args.question}")


if __name__ == "__main__":
    main()
