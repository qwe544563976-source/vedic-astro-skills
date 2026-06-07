#!/usr/bin/env python3
"""
setup_env.py — vedic-calculator 环境自动搭建脚本
跨平台（Windows / macOS / Linux），自动创建 venv 并按正确顺序安装依赖。

用法（AI 自动运行，用户也可手动）：
  python setup_env.py              # 在 scripts/ 同级创建 venv/
  python setup_env.py --target /path/to/dir   # 指定 venv 位置

安装顺序（关键！）：
  1. pysweph>=2.10.3.5     — 提供 swisseph module（社区活跃 fork，有 cp38~cp313 wheel）
  2. dashaflow>=0.3 --no-deps  — 跳过其对已停更的 pyswisseph 的声明依赖
  3. PyJHora==4.8.6        — SAV/BAV + Shadbala + 分盘
  4. pytz>=2024.1          — 时区
"""

import subprocess
import sys
import os
import platform
import shutil
import argparse


# ── 配置 ────────────────────────────────────────────
REQUIRED_PACKAGES = [
    # (包名, 版本约束, 额外 pip 参数)
    ("pysweph", ">=2.10.3.5", []),
    ("pytz", ">=2024.1", []),
    ("dashaflow", ">=0.3", ["--no-deps"]),
    ("PyJHora", "==4.8.6", []),
]

MIN_PYTHON = (3, 8)
MAX_PYTHON = (3, 13)
VENV_DIR_NAME = "venv"


# ── 工具函数 ──────────────────────────────────────────

def log(msg, level="INFO"):
    icons = {"INFO": "ℹ️", "OK": "✅", "WARN": "⚠️", "ERR": "❌"}
    print(f"  {icons.get(level, '·')} {msg}")


def find_python():
    """找到一个 3.8~3.13 的 Python 解释器"""
    # 1. 当前 Python 是否合格
    v = sys.version_info
    if MIN_PYTHON <= (v.major, v.minor) <= MAX_PYTHON:
        return sys.executable

    # 2. Windows: py launcher
    if platform.system() == "Windows":
        for minor in range(MAX_PYTHON[1], MIN_PYTHON[1] - 1, -1):
            try:
                result = subprocess.run(
                    ["py", f"-3.{minor}", "--version"],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    return f"py -3.{minor}"
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue

    # 3. Unix: python3.xx
    for minor in range(MAX_PYTHON[1], MIN_PYTHON[1] - 1, -1):
        name = f"python3.{minor}"
        if shutil.which(name):
            return name

    # 4. Generic python3
    if shutil.which("python3"):
        try:
            result = subprocess.run(
                ["python3", "-c", "import sys; print(sys.version_info.minor)"],
                capture_output=True, text=True, timeout=5
            )
            minor = int(result.stdout.strip())
            if MIN_PYTHON[1] <= minor <= MAX_PYTHON[1]:
                return "python3"
        except Exception:
            pass

    return None


def get_venv_python(venv_dir):
    """返回 venv 内的 python 路径"""
    if platform.system() == "Windows":
        return os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        return os.path.join(venv_dir, "bin", "python")


def get_venv_pip(venv_dir):
    """返回 venv 内的 pip 路径"""
    if platform.system() == "Windows":
        return os.path.join(venv_dir, "Scripts", "pip.exe")
    else:
        return os.path.join(venv_dir, "bin", "pip")


def run_cmd(cmd, desc=""):
    """运行命令并检查返回值"""
    if isinstance(cmd, str):
        cmd = cmd.split()
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        log(f"{desc} 失败: {result.stderr[-500:]}", "ERR")
        return False
    return True


def create_venv(python_cmd, venv_dir):
    """创建 venv"""
    log(f"创建 venv: {venv_dir}")
    cmd = python_cmd.split() + ["-m", "venv", venv_dir]
    return run_cmd(cmd, "创建 venv")


def install_packages(venv_dir):
    """按正确顺序安装依赖"""
    pip = get_venv_pip(venv_dir)
    
    # 先升级 pip
    py = get_venv_python(venv_dir)
    run_cmd([py, "-m", "pip", "install", "--upgrade", "pip"], "升级 pip")

    for pkg_name, version_spec, extra_args in REQUIRED_PACKAGES:
        pkg_str = f"{pkg_name}{version_spec}"
        log(f"安装 {pkg_str} {' '.join(extra_args)}")
        cmd = [pip, "install", pkg_str] + extra_args
        if not run_cmd(cmd, f"安装 {pkg_name}"):
            return False
    return True


def validate(venv_dir):
    """验证安装结果"""
    py = get_venv_python(venv_dir)
    
    # 1. 基础 import 检查
    checks = [
        ("swisseph", "import swisseph as swe; print(swe.version)"),
        ("dashaflow", "import dashaflow; print('OK')"),
        ("jhora", "import jhora; print('OK')"),
        ("pytz", "import pytz; print('OK')"),
    ]
    
    all_ok = True
    for name, code in checks:
        result = subprocess.run(
            [py, "-c", code], capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            log(f"{name}: {result.stdout.strip()}", "OK")
        else:
            log(f"{name}: import 失败", "ERR")
            all_ok = False
    
    if not all_ok:
        return False
    
    # 2. SAV=337 校验（用 ashtakavarga_pyjhora 直接测试）
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    test_code = f"""
import sys
sys.path.insert(0, r'{scripts_dir}')
from ashtakavarga_pyjhora import calculate_ashtakavarga_fixed
r = calculate_ashtakavarga_fixed(2002, 12, 11, 20, 47, 25.4333, 119.0, 8.0)
total = sum(r['sarvashtakavarga'].values())
print(total)
"""
    result = subprocess.run([py, "-c", test_code], capture_output=True, text=True, timeout=60)
    if result.returncode == 0 and result.stdout.strip() == "337":
        log("SAV=337 校验通过", "OK")
    else:
        log(f"SAV 校验失败 (got: {result.stdout.strip()}, err: {result.stderr[-200:]})", "ERR")
        return False
    
    return True


# ── 主流程 ──────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="vedic-calculator 环境自动搭建")
    parser.add_argument("--target", default=None, help="venv 创建目录（默认：scripts 同级）")
    args = parser.parse_args()

    print("\n🔧 vedic-calculator 环境搭建\n")

    # 确定 venv 位置
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(scripts_dir)  # vedic-calculator/
    venv_dir = args.target or os.path.join(skill_dir, VENV_DIR_NAME)

    # 检查是否已存在且可用
    venv_py = get_venv_python(venv_dir)
    if os.path.exists(venv_py):
        log(f"发现已有 venv: {venv_dir}")
        if validate(venv_dir):
            log("环境已就绪，无需重新安装", "OK")
            print(f"\n✅ Python: {venv_py}")
            return 0
        else:
            log("已有 venv 验证失败，重新安装依赖", "WARN")
            if not install_packages(venv_dir):
                return 1
            if validate(venv_dir):
                log("重新安装后验证通过", "OK")
                print(f"\n✅ Python: {venv_py}")
                return 0
            return 1

    # 查找合适的 Python
    python_cmd = find_python()
    if not python_cmd:
        log(f"未找到 Python {MIN_PYTHON[1]}~{MAX_PYTHON[1]}。请安装 Python 3.12 或 3.13。", "ERR")
        log("下载: https://www.python.org/downloads/", "ERR")
        return 1
    log(f"使用 Python: {python_cmd}")

    # 创建 venv
    if not create_venv(python_cmd, venv_dir):
        return 1

    # 安装依赖
    if not install_packages(venv_dir):
        return 1

    # 验证
    if not validate(venv_dir):
        return 1

    print(f"\n✅ 环境搭建完成！")
    print(f"   Python: {venv_py}")
    print(f"   使用方法: {venv_py} your_script.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
