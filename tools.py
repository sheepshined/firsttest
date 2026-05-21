"""
代码审查 Agent 的工具集。
每个工具包含两部分：API 定义（给模型看）和执行函数（实际运行）。
"""
'git测试'
import subprocess
import ast
import os


# ============================================================
# 工具定义 —— 告诉模型每个工具叫什么、有什么用、参数是什么
# ============================================================

TOOLS = [
    {
        "name": "read_file",
        "description": "读取指定文件的全部内容。用于获取待审查代码的完整文本。",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "要读取的文件路径，可以是相对路径或绝对路径",
                }
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "search_code",
        "description": (
            "在项目目录中搜索指定文本模式，返回匹配的文件名和行号。"
            "用于在审查时查找某个函数/类的定义、调用位置、或相关引用。"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "要搜索的文本模式，支持正则表达式",
                },
                "file_filter": {
                    "type": "string",
                    "description": "可选，限定搜索的文件类型，如 '*.py'。不填则搜索所有文件",
                },
            },
            "required": ["pattern"],
        },
    },
    {
        "name": "run_command",
        "description": (
            "在项目目录下执行一条 shell 命令，返回命令的输出。"
            "用于运行 pylint、mypy、pytest 等检查工具。"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "要执行的命令，如 'pylint myfile.py' 或 'python -m py_compile myfile.py'",
                }
            },
            "required": ["command"],
        },
    },
    {
        "name": "ast_analyze",
        "description": (
            "用 Python AST 模块解析一个 Python 文件的结构，"
            "返回所有函数、类、导入的概览，以及每个函数的行数和嵌套深度。"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "要分析的 Python 文件路径",
                }
            },
            "required": ["file_path"],
        },
    },
]


# ============================================================
# 工具执行 —— 真正干活的函数
# ============================================================

def read_file(file_path: str) -> str:
    """读取文件内容，返回带行号的文本。"""
    if not os.path.exists(file_path):
        return f"错误：文件不存在 —— {file_path}"

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        return f"错误：无法以 UTF-8 编码读取文件 —— {file_path}"

    output_parts = [f"=== {file_path} （共 {len(lines)} 行）===\n"]
    for i, line in enumerate(lines, start=1):
        output_parts.append(f"{i:>4} | {line.rstrip()}")
    return "\n".join(output_parts)


def search_code(pattern: str, file_filter: str = None) -> str:
    """在项目目录中搜索文本模式。"""
    import glob
    import re

    try:
        compiled = re.compile(pattern)
    except re.Error as e:
        return f"错误：无效的正则表达式 —— {e}"

    target_files = glob.glob(file_filter or "**/*", recursive=True)
    if not target_files:
        return f"错误：没有匹配到 {file_filter or '*'} 文件"

    results = []
    for file_path in target_files:
        if not os.path.isfile(file_path):
            continue
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line_no, line in enumerate(f, start=1):
                    if compiled.search(line):
                        results.append(f"{file_path}:{line_no} | {line.strip()[:120]}")
        except (UnicodeDecodeError, PermissionError):
            continue

    if not results:
        return f"未找到匹配 '{pattern}' 的内容"

    output = [f"=== 搜索 '{pattern}' 的结果 （共 {len(results)} 处）===\n"]
    output.extend(results[:50])  # 最多返回 50 条
    if len(results) > 50:
        output.append(f"\n... 还有 {len(results) - 50} 条结果未显示")
    return "\n".join(output)


def run_command(command: str) -> str:
    """执行 shell 命令并返回输出。"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.getcwd(),
        )
        output = []
        if result.stdout:
            output.append(result.stdout.strip())
        if result.stderr:
            output.append(result.stderr.strip())
        if not output:
            output.append(f"命令执行完毕，退出码: {result.returncode}")
        return "\n".join(output)
    except subprocess.TimeoutExpired:
        return "错误：命令执行超时（30 秒）"
    except Exception as e:
        return f"错误：命令执行失败 —— {e}"


def ast_analyze(file_path: str) -> str:
    """用 AST 解析 Python 文件结构。"""
    if not os.path.exists(file_path):
        return f"错误：文件不存在 —— {file_path}"

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
    except UnicodeDecodeError:
        return f"错误：无法以 UTF-8 编码读取文件 —— {file_path}"

    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError as e:
        return f"错误：文件有语法错误，无法解析 —— {e}"

    output_parts = [f"=== AST 结构分析：{file_path} ===\n"]

    # 导入
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(f"import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            names = ", ".join(a.name for a in node.names)
            imports.append(f"from {node.module} import {names}")
    if imports:
        output_parts.append("【导入模块】")
        output_parts.extend(f"  {imp}" for imp in imports)
        output_parts.append("")

    # 类
    classes = [node for node in ast.iter_child_nodes(tree) if isinstance(node, ast.ClassDef)]
    if classes:
        output_parts.append("【类】")
        for cls in classes:
            methods = [n for n in ast.iter_child_nodes(cls) if isinstance(n, ast.FunctionDef)]
            output_parts.append(f"  class {cls.name} （{len(methods)} 个方法，行 {cls.lineno}-{cls.end_lineno}）")
            for method in methods:
                depth = _max_nesting_depth(method)
                output_parts.append(f"    def {method.name}() —— {_count_lines(method)} 行，最大嵌套 {depth} 层")
        output_parts.append("")

    # 顶层函数
    functions = [node for node in ast.iter_child_nodes(tree) if isinstance(node, ast.FunctionDef)]
    if functions:
        output_parts.append("【顶层函数】")
        for func in functions:
            depth = _max_nesting_depth(func)
            output_parts.append(f"  def {func.name}() —— {_count_lines(func)} 行，最大嵌套 {depth} 层")
        output_parts.append("")

    if not classes and not functions:
        output_parts.append("（未发现函数或类定义）")

    return "\n".join(output_parts)


# ============================================================
# 辅助函数
# ============================================================

def _count_lines(node: ast.AST) -> int:
    """计算 AST 节点的代码行数。"""
    if hasattr(node, "end_lineno") and node.end_lineno is not None:
        return node.end_lineno - node.lineno + 1
    return 1


def _max_nesting_depth(node: ast.AST) -> int:
    """计算函数/方法的最大嵌套深度。"""
    max_depth = 0

    class DepthVisitor(ast.NodeVisitor):
        def visit_If(self, n):
            nonlocal max_depth
            d = self._depth_of(n)
            max_depth = max(max_depth, d)
            self.generic_visit(n)

        def visit_For(self, n):
            nonlocal max_depth
            d = self._depth_of(n)
            max_depth = max(max_depth, d)
            self.generic_visit(n)

        def visit_While(self, n):
            nonlocal max_depth
            d = self._depth_of(n)
            max_depth = max(max_depth, d)
            self.generic_visit(n)

        def _depth_of(self, target):
            depth = 0
            current = target
            while current is not None:
                if isinstance(current, (ast.If, ast.For, ast.While, ast.Try)):
                    depth += 1
                current = getattr(current, "parent", None)
            return depth

    # 给所有节点挂上 parent 引用
    for child in ast.walk(node):
        for grandchild in ast.iter_child_nodes(child):
            grandchild.parent = child  # type: ignore

    DepthVisitor().visit(node)
    return max_depth


# ============================================================
# 工具调度 —— 根据工具名调用对应的执行函数
# ============================================================

TOOL_MAP = {
    "read_file": read_file,
    "search_code": search_code,
    "run_command": run_command,
    "ast_analyze": ast_analyze,
}


def execute_tool(name: str, args: dict) -> str:
    """根据工具名和参数执行工具，返回结果字符串。"""
    if name not in TOOL_MAP:
        return f"错误：未知工具 —— {name}"
    func = TOOL_MAP[name]
    try:
        return func(**args)
    except TypeError as e:
        return f"错误：工具参数不匹配 —— {e}"
