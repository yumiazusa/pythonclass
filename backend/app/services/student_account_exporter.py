from datetime import datetime
from io import BytesIO

from openpyxl import Workbook

STUDENT_ACCOUNT_EXPORT_FILENAME = "学生账号清单.xlsx"
DEFAULT_PASSWORD_NOTE = "初始密码统一为123456，请首次登录后及时修改。"


def _format_datetime(value: datetime | None) -> str:
    if not value:
        return ""
    return value.strftime("%Y-%m-%d %H:%M:%S")


def build_student_accounts_export_bytes(rows: list[dict]) -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "学生账号"
    sheet.append(["姓名", "学号", "班级", "用户名", "账号状态", "创建时间", "密码说明"])

    for row in rows:
        enabled = bool(row.get("is_enabled"))
        sheet.append(
            [
                row.get("full_name") or "",
                row.get("student_no") or "",
                row.get("class_name") or "",
                row.get("username") or "",
                "启用" if enabled else "停用",
                _format_datetime(row.get("created_at")),
                DEFAULT_PASSWORD_NOTE,
            ]
        )

    output = BytesIO()
    workbook.save(output)
    return output.getvalue()
