from io import BytesIO

from openpyxl import Workbook

STUDENT_IMPORT_TEMPLATE_FILENAME = "学生名单导入模板.xlsx"


def build_student_import_template_bytes() -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "学生名单模板"
    sheet.append(["班级", "学号", "姓名"])
    sheet.append(["大数据2024级1班", "20240001", "张三"])
    sheet.append(["大数据2024级1班", "20240002", "李四"])

    output = BytesIO()
    workbook.save(output)
    return output.getvalue()
