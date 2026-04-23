import ast
import subprocess
import sys
import tempfile
import threading
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

IMAGE_MARKERS = ("__IMAGE_BASE64__=", "__PLOT_BASE64__=")

PLOT_CAPTURE_SNIPPET = """
try:
    import base64 as __b64
    import glob as __glob
    import io as __io
    import logging as __logging
    import os as __os
    import warnings as __warnings
    import matplotlib as __mpl
    from matplotlib import font_manager as __fm
    import matplotlib.pyplot as __plt

    # Suppress noisy matplotlib font warnings in runner stderr.
    __warnings.filterwarnings("ignore", message=r"Glyph .* missing from font\\(s\\).*", category=UserWarning)
    __logging.getLogger("matplotlib.font_manager").setLevel(__logging.ERROR)

    # Auto-pick a Chinese-capable font if available.
    # 1) Explicitly register common font file locations (macOS/Linux/Homebrew).
    __font_file_patterns = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/Library/Fonts/*.ttf",
        "/Library/Fonts/*.ttc",
        "/Library/Fonts/*.otf",
        __os.path.expanduser("~/Library/Fonts/*.ttf"),
        __os.path.expanduser("~/Library/Fonts/*.ttc"),
        __os.path.expanduser("~/Library/Fonts/*.otf"),
        "/opt/homebrew/share/fonts/**/*.ttf",
        "/opt/homebrew/share/fonts/**/*.ttc",
        "/opt/homebrew/share/fonts/**/*.otf",
        "/usr/share/fonts/**/*.ttf",
        "/usr/share/fonts/**/*.ttc",
        "/usr/share/fonts/**/*.otf",
    ]
    __font_keywords = ("NotoSansCJK", "Noto Sans CJK", "SourceHanSans", "PingFang", "Hiragino", "WenQuanYi", "SimHei", "Microsoft YaHei")
    for __pattern in __font_file_patterns:
        for __font_path in __glob.glob(__pattern, recursive=True):
            __name_lower = __os.path.basename(__font_path).lower()
            if not any(__kw.lower().replace(" ", "") in __name_lower.replace(" ", "") for __kw in __font_keywords):
                # Keep Library fonts broad (may still include Arial Unicode).
                if "/Library/Fonts/" not in __font_path and "/System/Library/Fonts/" not in __font_path:
                    continue
            try:
                __fm.fontManager.addfont(__font_path)
            except Exception:
                pass

    # 2) Reload and resolve a usable Chinese font family name.
    try:
        __fm._load_fontmanager(try_read_cache=False)
    except Exception:
        pass
    def __has_cjk_glyphs(__font_path):
        try:
            from matplotlib import ft2font as __ft2font

            __charmap = __ft2font.FT2Font(__font_path).get_charmap()
            return all(ord(__ch) in __charmap for __ch in ("中", "门", "店", "销", "售"))
        except Exception:
            return False

    __selected_font_name = None
    __preferred_names = (
        "WenQuanYi Zen Hei",
        "WenQuanYi Micro Hei",
        "Noto Sans CJK SC",
        "Source Han Sans CN",
        "PingFang SC",
        "Hiragino Sans GB",
        "Heiti SC",
        "STHeiti",
        "Microsoft YaHei",
        "SimHei",
        "Arial Unicode MS",
    )

    # Pass 1: preferred family names + real glyph coverage.
    for __name in __preferred_names:
        for __font in __fm.fontManager.ttflist:
            if __font.name == __name and __has_cjk_glyphs(__font.fname):
                __selected_font_name = __font.name
                break
        if __selected_font_name:
            break

    # Pass 2: any installed font that contains core CJK glyphs.
    if not __selected_font_name:
        for __font in __fm.fontManager.ttflist:
            if __has_cjk_glyphs(__font.fname):
                __selected_font_name = __font.name
                break

    __edu_cjk_font_name = __selected_font_name
    if __selected_font_name:
        __mpl.rcParams["font.family"] = [__selected_font_name]
        __mpl.rcParams["font.sans-serif"] = [__selected_font_name, "DejaVu Sans"]
        __mpl.rcParams["axes.unicode_minus"] = False

    if "__edu_plot_images__" not in dir():
        __edu_plot_images__ = []

    def __edu_capture_open_figures(close_after=False):
        for __fig_num in list(__plt.get_fignums()):
            __fig = __plt.figure(__fig_num)
            if "__edu_cjk_font_name" in dir() and __edu_cjk_font_name:
                try:
                    for __text in list(__fig.texts):
                        __text.set_fontfamily(__edu_cjk_font_name)
                    for __ax in __fig.get_axes():
                        __ax.title.set_fontfamily(__edu_cjk_font_name)
                        __ax.xaxis.label.set_fontfamily(__edu_cjk_font_name)
                        __ax.yaxis.label.set_fontfamily(__edu_cjk_font_name)
                        for __lbl in list(__ax.get_xticklabels()) + list(__ax.get_yticklabels()):
                            __lbl.set_fontfamily(__edu_cjk_font_name)
                        __legend = __ax.get_legend()
                        if __legend:
                            for __txt in __legend.get_texts():
                                __txt.set_fontfamily(__edu_cjk_font_name)
                except Exception:
                    pass
            __buf = __io.BytesIO()
            __fig.savefig(__buf, format="png", bbox_inches="tight")
            __buf.seek(0)
            __edu_plot_images__.append(__b64.b64encode(__buf.read()).decode("utf-8"))
            __buf.close()
            if close_after:
                __plt.close(__fig)

    def __edu_show(*args, **kwargs):
        __edu_capture_open_figures(close_after=True)
        return None

    __plt.show = __edu_show
except Exception:
    pass
"""

PLOT_FLUSH_SNIPPET = """
try:
    if "__edu_capture_open_figures" in dir():
        __edu_capture_open_figures(close_after=False)
    if "__edu_plot_images__" in dir():
        for __img in __edu_plot_images__:
            print("__IMAGE_BASE64__=" + __img)
except Exception:
    pass
"""

_RUN_SEMAPHORE: threading.BoundedSemaphore | None = None
_RUN_SEMAPHORE_LIMIT: int | None = None
_RUN_SEMAPHORE_LOCK = threading.Lock()


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


def _clean_matplotlib_font_warnings(stderr: str) -> str:
    if not stderr:
        return stderr
    cleaned_lines: list[str] = []
    for line in stderr.splitlines():
        text = line.strip()
        if "missing from font(s)" in text and "Glyph" in text:
            continue
        if text.startswith("findfont: Generic family"):
            continue
        cleaned_lines.append(line)
    cleaned_stderr = "\n".join(cleaned_lines)
    if stderr.endswith("\n") and cleaned_stderr:
        cleaned_stderr += "\n"
    return cleaned_stderr


def _inject_plot_capture(code: str) -> str:
    return "import matplotlib\nmatplotlib.use('Agg')\n\n" + PLOT_CAPTURE_SNIPPET + "\n\n" + code + "\n\n" + PLOT_FLUSH_SNIPPET


def _extract_images_from_stdout(stdout: str) -> tuple[str, list[str]]:
    if not stdout:
        return "", []
    image_base64_list: list[str] = []
    clean_lines: list[str] = []
    for line in stdout.splitlines():
        matched = False
        for marker in IMAGE_MARKERS:
            idx = line.find(marker)
            if idx >= 0:
                payload = line[idx + len(marker) :].strip()
                if payload:
                    image_base64_list.append(payload)
                matched = True
                break
        if not matched:
            clean_lines.append(line)
    cleaned_stdout = "\n".join(clean_lines)
    if stdout.endswith("\n"):
        cleaned_stdout += "\n"
    return cleaned_stdout, image_base64_list


def _get_run_semaphore(concurrency_limit: int) -> threading.BoundedSemaphore:
    global _RUN_SEMAPHORE, _RUN_SEMAPHORE_LIMIT
    limit = max(1, int(concurrency_limit))
    with _RUN_SEMAPHORE_LOCK:
        if _RUN_SEMAPHORE is None or _RUN_SEMAPHORE_LIMIT != limit:
            _RUN_SEMAPHORE = threading.BoundedSemaphore(value=limit)
            _RUN_SEMAPHORE_LIMIT = limit
        return _RUN_SEMAPHORE


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

    run_semaphore = _get_run_semaphore(settings.code_run_concurrency_limit)
    queue_wait_seconds = max(1, int(settings.code_run_queue_wait_seconds))
    acquired = run_semaphore.acquire(timeout=queue_wait_seconds)
    if not acquired:
        return CodeRunResponse(
            success=False,
            status="internal_error",
            stdout="",
            stderr=f"当前运行任务较多，请稍后重试（排队超过 {queue_wait_seconds} 秒）",
            image_base64=None,
            images_base64=None,
            returncode=None,
            timed_out=False,
            execution_time_ms=0,
            blocked=False,
            block_reason=None,
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
            temp_file.write(_inject_plot_capture(code))
            temp_file_path = temp_file.name

        completed_process = subprocess.run(
            [sys.executable, temp_file_path],
            capture_output=True,
            text=True,
            timeout=settings.code_run_timeout_seconds,
        )
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        stdout_cleaned, image_base64_list = _extract_images_from_stdout(completed_process.stdout or "")
        stdout = _truncate_output(stdout_cleaned, settings.code_run_max_output_chars)
        stderr = _truncate_output(
            _clean_matplotlib_font_warnings(completed_process.stderr or ""),
            settings.code_run_max_output_chars,
        )
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
            image_base64=image_base64_list[-1] if image_base64_list else None,
            images_base64=image_base64_list or None,
            returncode=completed_process.returncode,
            timed_out=False,
            execution_time_ms=elapsed_ms,
            blocked=False,
            block_reason=None,
        )
    except subprocess.TimeoutExpired as exc:
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        stdout_cleaned, image_base64_list = _extract_images_from_stdout(exc.stdout or "")
        stdout = _truncate_output(stdout_cleaned, settings.code_run_max_output_chars)
        stderr = _truncate_output(_clean_matplotlib_font_warnings(exc.stderr or ""), settings.code_run_max_output_chars)
        return CodeRunResponse(
            success=False,
            status="timed_out",
            stdout=stdout,
            stderr=stderr,
            image_base64=image_base64_list[-1] if image_base64_list else None,
            images_base64=image_base64_list or None,
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
            image_base64=None,
            images_base64=None,
            returncode=None,
            timed_out=False,
            execution_time_ms=elapsed_ms,
            blocked=False,
            block_reason=None,
        )
    finally:
        if temp_file_path:
            Path(temp_file_path).unlink(missing_ok=True)
        if acquired:
            run_semaphore.release()
