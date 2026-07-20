#!/usr/bin/env python3
"""
PreToolUse 钩子(强制前台同步,matcher=Agent)。

在 Agent 工具(派子任务)真正执行之前,检查 tool_input.run_in_background:
  - 缺省,或值不是严格意义上的布尔 false(包括 true、字符串 "false"、null 等)
    一律视为违规 —— 拦截,要求显式写 run_in_background:false。
  - run_in_background 严格等于 false 时放行。

目的:防止子任务在后台跑完之后只交一份"吹牛回执",主模型没有盯着回执就继续推进。

边界情况:守门员脚本自身出错(stdin 不是合法 JSON 等)时,一律放行并向 stderr
打一行警告 —— 守门员坏了不能把正门焊死。
"""
import json
import sys

BLOCK_REASON = (
    "【拦截】派子任务必须前台同步:请显式设置 run_in_background:false,"
    "主窗口盯完回执再推进。另:子任务回执必须附带证据(提交哈希/测试输出/文件路径),"
    "无证据回执按偷懒退回。"
)


def emit(decision: str, reason: str) -> None:
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        }
    }
    print(json.dumps(output, ensure_ascii=False))


def warn_and_allow(message: str) -> int:
    print(f"[agent-foreground-gate 警告] {message}", file=sys.stderr)
    emit("allow", f"守门员脚本异常,已放行(警告:{message})")
    return 0


def main() -> int:
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception as exc:
        return warn_and_allow(f"stdin JSON 解析失败:{exc}")

    tool_input = data.get("tool_input")
    if not isinstance(tool_input, dict):
        tool_input = {}

    run_in_background = tool_input.get("run_in_background")

    if run_in_background is False:
        emit("allow", "run_in_background 显式为 false,前台同步,放行")
        return 0

    emit("deny", BLOCK_REASON)
    return 0


if __name__ == "__main__":
    sys.exit(main())
