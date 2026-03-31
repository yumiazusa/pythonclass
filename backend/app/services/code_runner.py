import ast
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from app.core.config import get_settings
from app.schemas.code_run import CodeRunResponse

DANGEROUS_IMPORTS = {
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
DANGEROUS_CALLS = {
    "eval",
    "exec",
    "compile",
    "open",
    "__import__",
    "input",
    "globals",
    "locals",
    "vars",
    "getattr",
    "setattr",
    "delattr",
    "breakpoint",
    "quit",
    "exit",
}


def _check_blocked(code: str) -> str | None:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_name = alias.name.split(".")[0]
                if module_name in DANGEROUS_IMPORTS:
                    return f"Blocked dangerous import: {module_name}"
        if isinstance(node, ast.ImportFrom) and node.module:
            module_name = node.module.split(".")[0]
            if module_name in DANGEROUS_IMPORTS:
                return f"Blocked dangerous import: {module_name}"
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            call_name = node.func.id
            if call_name in DANGEROUS_CALLS:
                return f"Blocked dangerous builtin: {call_name}"
    return None


def _truncate_output(output: str, max_chars: int) -> str:
    if len(output) <= max_chars:
        return output
    return output[:max_chars] + "\n...[TRUNCATED]"


def run_python_code(code: str) -> CodeRunResponse:
    settings = get_settings()
    block_reason = _check_blocked(code)
    if block_reason:
        return CodeRunResponse(
            success=False,
            status="blocked",
            stdout="",
            stderr="",
            returncode=None,
            timed_out=False,
            execution_time_ms=0,
            blocked=True,
            block_reason=block_reason,
        )

    temp_dir = Path(settings.code_run_temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)

    start_time = time.perf_counter()
    temp_file_path = ""
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".py",
            delete=False,
            dir=str(temp_dir),
        ) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name

        completed_process = subprocess.run(
            [sys.executable, temp_file_path],
            capture_output=True,
            text=True,
            timeout=settings.code_run_timeout_seconds,
        )
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        stdout = _truncate_output(completed_process.stdout or "", settings.code_run_max_output_chars)
        stderr = _truncate_output(completed_process.stderr or "", settings.code_run_max_output_chars)
        if completed_process.returncode == 0:
            status = "completed"
            success = True
        else:
            status = "runtime_error"
            success = False
        return CodeRunResponse(
            success=success,
            status=status,
            stdout=stdout,
            stderr=stderr,
            returncode=completed_process.returncode,
            timed_out=False,
            execution_time_ms=elapsed_ms,
            blocked=False,
            block_reason=None,
        )
    except subprocess.TimeoutExpired as exc:
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        stdout = _truncate_output(exc.stdout or "", settings.code_run_max_output_chars)
        stderr = _truncate_output(exc.stderr or "", settings.code_run_max_output_chars)
        return CodeRunResponse(
            success=False,
            status="timed_out",
            stdout=stdout,
            stderr=stderr,
            returncode=None,
            timed_out=True,
            execution_time_ms=elapsed_ms,
            blocked=False,
            block_reason=None,
        )
    except Exception as exc:
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        return CodeRunResponse(
            success=False,
            status="internal_error",
            stdout="",
            stderr=str(exc),
            returncode=None,
            timed_out=False,
            execution_time_ms=elapsed_ms,
            blocked=False,
            block_reason=None,
        )
    finally:
        if temp_file_path:
            Path(temp_file_path).unlink(missing_ok=True)
