#!/usr/bin/env python3
"""
PreToolUse 钩子(硬性守门员,matcher=Workflow)。

在 Workflow 工具真正执行之前,解析 tool_input 里的脚本文本:
  - 优先取 tool_input.script;若不存在则尝试读取 tool_input.scriptPath 指向的文件。
  - 用粗略正则统计 `agent(` 调用次数 N。
  - 用粗略正则统计 `model:` / `model =` / `agentType:` / `agentType =` 出现次数 M
    (这是启发式统计,不是真正的语法解析,可能有轻微偏差)。
  - 若 N>0 且 M<N:拦截,通过 hookSpecificOutput.permissionDecision="deny" 返回
    中文拦截理由。
  - 若 resumeFromRunId 存在,或 N==0:放行。

边界情况:守门员脚本自身出错(stdin 不是合法 JSON、scriptPath 读取失败等)时,
一律放行并向 stderr 打一行警告 —— 守门员坏了不能把正门焊死。
"""
import json
import re
import sys

AGENT_CALL_PATTERN = re.compile(r"agent\s*\(")
MODEL_DECL_PATTERN = re.compile(r"(model\s*:|model\s*=|agentType\s*:|agentType\s*=)")


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
    print(f"[workflow-model-gate 警告] {message}", file=sys.stderr)
    emit("allow", f"守门员脚本异常,已放行(警告:{message})")
    return 0


def main() -> int:
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception as exc:
        return warn_and_allow(f"stdin JSON 解析失败:{exc}")

    tool_input = data.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        return warn_and_allow("tool_input 不是对象类型")

    if tool_input.get("resumeFromRunId"):
        emit("allow", "resumeFromRunId 存在,视为恢复运行,放行")
        return 0

    script = tool_input.get("script")
    if script is None:
        script_path = tool_input.get("scriptPath")
        if script_path:
            try:
                with open(script_path, "r", encoding="utf-8") as f:
                    script = f.read()
            except Exception as exc:
                return warn_and_allow(f"读取 scriptPath 失败({script_path}):{exc}")
        else:
            script = ""

    if not isinstance(script, str):
        return warn_and_allow("script 字段不是字符串类型")

    n = len(AGENT_CALL_PATTERN.findall(script))
    m = len(MODEL_DECL_PATTERN.findall(script))

    if n == 0:
        emit("allow", "脚本中没有 agent() 子任务,放行")
        return 0

    if m < n:
        reason = (
            f"【拦截】workflow 脚本里有 {n} 个 agent() 子任务,只有 {m} 个显式指定了 "
            f"model/agentType。每个子任务必须写明模型(默认 sonnet),防止全员继承主模型烧钱。"
            f"补齐后重试。(启发式统计,基于粗略正则匹配 model:/model =/agentType:/agentType =)"
        )
        emit("deny", reason)
        return 0

    emit(
        "allow",
        f"脚本中 {n} 个 agent() 子任务均已显式指定 model/agentType({m} 处声明),放行",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
