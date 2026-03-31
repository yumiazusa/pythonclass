import ast
from dataclasses import dataclass

ALLOWED_IMPORT_MODULES = {
    "requests",
    "bs4",
    "pandas",
    "numpy",
    "matplotlib",
    "seaborn",
    "sklearn",
    "json",
    "re",
    "math",
    "statistics",
    "datetime",
}

FORBIDDEN_IMPORT_MODULES = {
    "os",
    "sys",
    "subprocess",
    "socket",
    "shutil",
    "pathlib",
    "ctypes",
    "multiprocessing",
    "threading",
}


@dataclass
class ImportValidationResult:
    valid: bool
    normalized_imports: list[str]
    errors: list[str]


def _extract_imported_modules(node: ast.stmt) -> list[str]:
    if isinstance(node, ast.Import):
        return [alias.name.split(".")[0] for alias in node.names]
    if isinstance(node, ast.ImportFrom):
        if not node.module:
            return []
        return [node.module.split(".")[0]]
    return []


def _validate_module(module_name: str) -> str | None:
    if module_name in FORBIDDEN_IMPORT_MODULES:
        return f"禁止导入危险库：{module_name}"
    if module_name not in ALLOWED_IMPORT_MODULES:
        return f"不在允许白名单内：{module_name}"
    return None


def _parse_single_import_line(line: str, line_no: int) -> tuple[str | None, list[str]]:
    stripped = line.strip()
    if not stripped:
        return None, []
    try:
        tree = ast.parse(stripped)
    except SyntaxError:
        return None, [f"第 {line_no} 行格式错误，仅支持 import / from ... import ..."]
    if len(tree.body) != 1:
        return None, [f"第 {line_no} 行仅允许一条导入语句"]
    node = tree.body[0]
    if not isinstance(node, (ast.Import, ast.ImportFrom)):
        return None, [f"第 {line_no} 行仅支持 import / from ... import ..."]
    modules = _extract_imported_modules(node)
    errors = []
    for module_name in modules:
        error = _validate_module(module_name)
        if error:
            errors.append(f"第 {line_no} 行：{error}")
    if errors:
        return None, errors
    return stripped, []


def validate_import_lines(lines: list[str]) -> ImportValidationResult:
    normalized: list[str] = []
    errors: list[str] = []
    seen = set()
    for index, line in enumerate(lines, start=1):
        statement, line_errors = _parse_single_import_line(line, index)
        if line_errors:
            errors.extend(line_errors)
            continue
        if not statement:
            continue
        if statement not in seen:
            normalized.append(statement)
            seen.add(statement)
    return ImportValidationResult(valid=len(errors) == 0, normalized_imports=normalized, errors=errors)


def validate_custom_import_text(raw_text: str) -> ImportValidationResult:
    lines = (raw_text or "").splitlines()
    return validate_import_lines(lines)


def validate_imports_in_code(code: str) -> ImportValidationResult:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return ImportValidationResult(valid=True, normalized_imports=[], errors=[])
    errors: list[str] = []
    normalized: list[str] = []
    seen = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            modules = _extract_imported_modules(node)
            for module_name in modules:
                error = _validate_module(module_name)
                if error:
                    line_no = getattr(node, "lineno", "?")
                    errors.append(f"第 {line_no} 行：{error}")
            statement = ast.get_source_segment(code, node) or ast.unparse(node)
            statement = statement.strip()
            if statement and statement not in seen:
                normalized.append(statement)
                seen.add(statement)
    return ImportValidationResult(valid=len(errors) == 0, normalized_imports=normalized, errors=errors)
