#!/usr/bin/env python3
"""
UserPromptSubmit 钩子(软性提示注入)。

读取 stdin 的 hook 输入 JSON,取其 "prompt" 字段;若其中出现
workflow / autocode / ultracode(不区分大小写),通过
hookSpecificOutput.additionalContext 注入一段固定中文提醒,
提示编排 workflow 时每个 agent() 子任务都要显式指定 model/agentType。

不命中时不输出任何内容(空 stdout),不影响正常提交流程。
任何解析异常都视为不命中,静默放行,不阻断用户输入。
"""
import json
import re
import sys

REMINDER = (
    "【模型分配提醒】编排 workflow 时,每个 agent() 子任务必须显式指定 model"
    "(默认 sonnet;纯机械誊抄可用 haiku;只有最难的判决/仲裁步才允许更高档)"
    "或 agentType。禁止让全部子任务继承主模型。"
)

TRIGGER_PATTERN = re.compile(r"workflow|autocode|ultracode", re.IGNORECASE)


def main() -> int:
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        # 输入无法解析时,不注入任何内容,静默放行。
        return 0

    prompt = data.get("prompt", "") or ""

    if TRIGGER_PATTERN.search(prompt):
        output = {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": REMINDER,
            }
        }
        print(json.dumps(output, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    sys.exit(main())
