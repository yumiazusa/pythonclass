from datetime import datetime
from io import BytesIO

from openpyxl import Workbook

EXPERIMENT_RESULT_EXPORT_FILENAME = "实验结果导出.xlsx"


def _format_datetime(value: datetime | None) -> str:
    if not value:
        return ""
    return value.strftime("%Y-%m-%d %H:%M:%S")


def _format_review_status(value: str | None) -> str:
    if value == "passed":
        return "通过"
    if value == "failed":
        return "未通过"
    return "待批阅"


def build_experiment_results_export_bytes(rows: list[dict]) -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "实验结果"
    sheet.append(
        [
            "姓名",
            "学号",
            "班级",
            "用户名",
            "最新提交ID",
            "最新版本号",
            "最新提交状态",
            "是否最终提交",
            "是否锁定",
            "批阅状态",
            "批阅时间",
            "最近更新时间",
        ]
    )

    for row in rows:
        sheet.append(
            [
                row.get("full_name") or "",
                row.get("student_no") or "",
                row.get("class_name") or "",
                row.get("username") or "",
                row.get("latest_submission_id") or "",
                row.get("latest_version") or "",
                row.get("latest_status") or "",
                "是" if row.get("has_final_submission") else "否",
                "是" if row.get("is_locked") else "否",
                _format_review_status(row.get("review_status")),
                _format_datetime(row.get("reviewed_at")),
                _format_datetime(row.get("latest_updated_at")),
            ]
        )

    output = BytesIO()
    workbook.save(output)
    return output.getvalue()
