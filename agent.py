"""
代码审查 Agent 的主逻辑 —— Agent Loop。
调用 DeepSeek V4 API，让模型自主决定何时使用工具。
"""

import json
import os
import sys

# 修复 Windows 终端中文乱码问题
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.rule import Rule
from rich.status import Status
from rich.table import Table

from prompt import SYSTEM_PROMPT
from tools import TOOLS, execute_tool

console = Console()

# ============================================================
# API 配置
# ============================================================

API_KEY = os.environ["DEEPSEEK-V4_API_KEY"]
BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-chat"

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


# ============================================================
# 工具定义转换
# ============================================================

def _to_openai_tools(tools: list[dict]) -> list[dict]:
    openai_tools = []
    for tool in tools:
        openai_tools.append({
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["input_schema"],
            },
        })
    return openai_tools


# ============================================================
# Agent Loop
# ============================================================

def review_file(file_path: str, max_turns: int = 10) -> str:
    """审查单个 Python 文件，返回审查报告。"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"请审查这个文件：{file_path}\n\n先读取文件内容，然后按照你的审查流程进行分析。",
        },
    ]

    openai_tools = _to_openai_tools(TOOLS)

    console.print()
    console.print(Panel(
        f"[bold white]{file_path}[/]",
        title="开始审查",
        border_style="blue",
    ))

    for turn in range(max_turns):
        with Status(f"[dim]分析中 (第 {turn + 1} 轮)...[/]", spinner="dots", console=console):
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=openai_tools,
            )

        msg = response.choices[0].message

        # 情况 1：模型调用工具
        if msg.tool_calls:
            console.print(f"[dim]第 {turn + 1} 轮 · 调用工具[/]")

            messages.append({
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in msg.tool_calls
                ],
            })

            for tc in msg.tool_calls:
                tool_name = tc.function.name
                tool_args = json.loads(tc.function.arguments)
                args_brief = _brief_args(tool_args)

                with Status(f"[dim]{tool_name} {args_brief}[/]", spinner="point", console=console):
                    result = execute_tool(tool_name, tool_args)

                console.print(f"  [green]OK[/] [bold]{tool_name}[/] {args_brief} [dim]({len(result)} 字符)[/]")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })

        # 情况 2：模型输出最终报告
        else:
            console.print()
            console.print(Rule("审查报告", style="blue"))
            console.print()
            md = Markdown(msg.content, code_theme="github-dark")
            console.print(md)
            console.print()
            return msg.content

    return "错误：Agent 在达到最大轮次后仍未完成审查"


# ============================================================
# 辅助函数
# ============================================================

def _brief_args(args: dict) -> str:
    """把工具参数压缩为简短显示，避免一行过长。"""
    parts = []
    for k, v in args.items():
        s = str(v)
        if len(s) > 60:
            s = s[:57] + "..."
        parts.append(f"{k}={s}")
    return ", ".join(parts)


# ============================================================
# 命令行入口
# ============================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        console.print("[red]用法：python agent.py <文件路径>[/]")
        sys.exit(1)

    target = sys.argv[1]
    review_file(target)
