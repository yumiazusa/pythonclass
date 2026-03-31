from urllib.parse import quote

from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status
from fastapi.responses import Response

from app.api.deps import CurrentTeacher, DBSession
from app.core.security import get_password_hash
from app.crud import crud_experiment, crud_teacher, crud_user
from app.schemas.experiment import ExperimentRead, ExperimentSettingsUpdate
from app.schemas.submission import CodeSubmissionHistoryItem
from app.schemas.teacher import (
    TeacherBatchReviewRequest,
    TeacherBatchReviewResponse,
    TeacherBatchReturnRequest,
    TeacherBatchReturnResponse,
    TeacherExperimentClassSummaryItem,
    TeacherExperimentOverviewItem,
    TeacherExperimentStudentStatusPage,
    TeacherExperimentStudentStatusItem,
    TeacherStudentAccountItem,
    TeacherStudentAccountPage,
    TeacherStudentBatchPasswordResetRequest,
    TeacherStudentBatchPasswordResetResponse,
    TeacherStudentBatchStatusRequest,
    TeacherStudentBatchStatusUpdateResponse,
    TeacherStudentImportResponse,
    TeacherStudentStatusUpdateResponse,
    TeacherSubmissionReviewUpdate,
    TeacherReturnResponse,
    TeacherSubmissionDetailRead,
)
from app.services.experiment_result_exporter import (
    EXPERIMENT_RESULT_EXPORT_FILENAME,
    build_experiment_results_export_bytes,
)
from app.services.student_account_exporter import STUDENT_ACCOUNT_EXPORT_FILENAME, build_student_accounts_export_bytes
from app.services.student_importer import import_students_from_excel
from app.services.student_import_template import (
    STUDENT_IMPORT_TEMPLATE_FILENAME,
    build_student_import_template_bytes,
)

router = APIRouter(prefix="/teacher", tags=["teacher"])
ALLOWED_STUDENT_SORT_BY = {"created_at", "username", "full_name", "student_no", "class_name", "is_enabled"}
ALLOWED_EXPERIMENT_STUDENT_SORT_BY = {"latest_updated_at", "username", "latest_version"}
ALLOWED_SORT_ORDER = {"asc", "desc"}


def _ensure_experiment_exists(db: DBSession, experiment_id: int) -> None:
    experiment = crud_experiment.get(db, experiment_id=experiment_id)
    if not experiment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="实验不存在")


def _ensure_user_exists(db: DBSession, user_id: int) -> None:
    user = crud_user.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")


def _validate_student_list_sort(sort_by: str, sort_order: str) -> None:
    if sort_by not in ALLOWED_STUDENT_SORT_BY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sort_by 参数仅支持 created_at/username/full_name/student_no/class_name/is_enabled",
        )
    if sort_order not in ALLOWED_SORT_ORDER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="sort_order 参数仅支持 asc/desc")


def _validate_experiment_student_list_params(status_filter: str, review_status_filter: str, sort_by: str, sort_order: str) -> None:
    if status_filter not in {"all", "draft", "submitted"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="status 参数仅支持 all/draft/submitted")
    if review_status_filter not in {"all", "pending", "passed", "failed"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="review_status 参数仅支持 all/pending/passed/failed")
    if sort_by not in ALLOWED_EXPERIMENT_STUDENT_SORT_BY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sort_by 参数仅支持 latest_updated_at/username/latest_version",
        )
    if sort_order not in ALLOWED_SORT_ORDER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="sort_order 参数仅支持 asc/desc")


def _batch_update_students_enabled_status(
    *,
    db: DBSession,
    user_ids: list[int],
    target_enabled: bool,
) -> tuple[list[int], list[dict]]:
    success_user_ids: list[int] = []
    failed_items: list[dict] = []
    seen_user_ids: set[int] = set()
    for user_id in user_ids:
        if user_id in seen_user_ids:
            continue
        seen_user_ids.add(user_id)
        user = crud_user.get_by_id(db, user_id=user_id)
        if not user:
            failed_items.append({"user_id": user_id, "reason": "用户不存在"})
            continue
        if user.role != "student":
            failed_items.append({"user_id": user_id, "reason": "仅支持学生账号"})
            continue
        try:
            with db.begin_nested():
                user.is_enabled = target_enabled
                db.add(user)
            success_user_ids.append(user_id)
        except Exception as exc:
            failed_items.append({"user_id": user_id, "reason": f"更新失败：{exc}"})
    db.commit()
    return success_user_ids, failed_items


@router.get("/experiments/overview", response_model=list[TeacherExperimentOverviewItem])
def get_teacher_experiments_overview(db: DBSession, teacher_user: CurrentTeacher) -> list[TeacherExperimentOverviewItem]:
    _ = teacher_user
    rows = crud_teacher.list_experiment_overview(db)
    return [TeacherExperimentOverviewItem.model_validate(item) for item in rows]


@router.patch("/experiments/{experiment_id}/settings", response_model=ExperimentRead)
def update_teacher_experiment_settings(
    experiment_id: int,
    settings_in: ExperimentSettingsUpdate,
    db: DBSession,
    teacher_user: CurrentTeacher,
) -> ExperimentRead:
    _ = teacher_user
    experiment = crud_experiment.get(db, experiment_id=experiment_id)
    if not experiment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="实验不存在")
    if settings_in.open_at and settings_in.due_at and settings_in.due_at <= settings_in.open_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="截止时间必须晚于开放时间")
    updated = crud_experiment.update_settings(db, experiment=experiment, settings_in=settings_in)
    return ExperimentRead.model_validate(updated)


@router.get(
    "/experiments/{experiment_id}/students",
    response_model=TeacherExperimentStudentStatusPage,
)
def get_teacher_experiment_students(
    experiment_id: int,
    db: DBSession,
    teacher_user: CurrentTeacher,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    keyword: str = Query(default=""),
    status_filter: str = Query(default="all", alias="status"),
    review_status_filter: str = Query(default="all", alias="review_status"),
    class_name: str = Query(default=""),
    student_no: str = Query(default=""),
    sort_by: str = Query(default="latest_updated_at"),
    sort_order: str = Query(default="desc"),
) -> TeacherExperimentStudentStatusPage:
    _ = teacher_user
    _ensure_experiment_exists(db, experiment_id=experiment_id)
    _validate_experiment_student_list_params(status_filter, review_status_filter, sort_by, sort_order)

    data = crud_teacher.list_experiment_student_latest_status(
        db,
        experiment_id=experiment_id,
        page=page,
        page_size=page_size,
        keyword=keyword,
        status_filter=status_filter,
        review_status_filter=review_status_filter,
        class_name=class_name,
        student_no=student_no,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return TeacherExperimentStudentStatusPage(
        items=[TeacherExperimentStudentStatusItem.model_validate(item) for item in data["items"]],
        total=data["total"],
        page=data["page"],
        page_size=data["page_size"],
        total_pages=data["total_pages"],
    )


@router.get("/experiments/{experiment_id}/export")
def export_teacher_experiment_students(
    experiment_id: int,
    db: DBSession,
    teacher_user: CurrentTeacher,
    keyword: str = Query(default=""),
    status_filter: str = Query(default="all", alias="status"),
    review_status_filter: str = Query(default="all", alias="review_status"),
    class_name: str = Query(default=""),
    student_no: str = Query(default=""),
    sort_by: str = Query(default="latest_updated_at"),
    sort_order: str = Query(default="desc"),
) -> Response:
    _ = teacher_user
    _ensure_experiment_exists(db, experiment_id=experiment_id)
    _validate_experiment_student_list_params(status_filter, review_status_filter, sort_by, sort_order)
    rows = crud_teacher.list_experiment_student_latest_status_for_export(
        db,
        experiment_id=experiment_id,
        keyword=keyword,
        status_filter=status_filter,
        review_status_filter=review_status_filter,
        class_name=class_name,
        student_no=student_no,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    file_bytes = build_experiment_results_export_bytes(rows)
    encoded_filename = quote(f"实验{experiment_id}_{EXPERIMENT_RESULT_EXPORT_FILENAME}")
    headers = {
        "Content-Disposition": (
            f'attachment; filename="experiment_{experiment_id}_results.xlsx"; '
            f"filename*=UTF-8''{encoded_filename}"
        ),
        "Cache-Control": "no-store",
    }
    return Response(
        content=file_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


@router.get(
    "/experiments/{experiment_id}/class-summary",
    response_model=list[TeacherExperimentClassSummaryItem],
)
def get_teacher_experiment_class_summary(
    experiment_id: int,
    db: DBSession,
    teacher_user: CurrentTeacher,
) -> list[TeacherExperimentClassSummaryItem]:
    _ = teacher_user
    _ensure_experiment_exists(db, experiment_id=experiment_id)
    rows = crud_teacher.get_experiment_class_summary(db, experiment_id=experiment_id)
    return [TeacherExperimentClassSummaryItem.model_validate(item) for item in rows]


@router.get(
    "/experiments/{experiment_id}/students/{user_id}/history",
    response_model=list[CodeSubmissionHistoryItem],
)
def get_teacher_student_history(
    experiment_id: int,
    user_id: int,
    db: DBSession,
    teacher_user: CurrentTeacher,
) -> list[CodeSubmissionHistoryItem]:
    _ = teacher_user
    _ensure_experiment_exists(db, experiment_id=experiment_id)
    _ensure_user_exists(db, user_id=user_id)
    rows = crud_teacher.list_student_history_by_experiment(db, experiment_id=experiment_id, user_id=user_id)
    return [CodeSubmissionHistoryItem.model_validate(item) for item in rows]


@router.get("/submissions/{submission_id}", response_model=TeacherSubmissionDetailRead)
def get_teacher_submission_detail(
    submission_id: int,
    db: DBSession,
    teacher_user: CurrentTeacher,
) -> TeacherSubmissionDetailRead:
    _ = teacher_user
    submission = crud_teacher.get_submission_detail(db, submission_id=submission_id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="提交记录不存在")
    return TeacherSubmissionDetailRead.model_validate(submission)


@router.post("/submissions/{submission_id}/review", response_model=TeacherSubmissionDetailRead)
def review_teacher_submission(
    submission_id: int,
    review_in: TeacherSubmissionReviewUpdate,
    db: DBSession,
    teacher_user: CurrentTeacher,
) -> TeacherSubmissionDetailRead:
    reviewed = crud_teacher.review_submission(
        db,
        submission_id=submission_id,
        reviewer_id=teacher_user.id,
        review_status=review_in.review_status,
        review_comment=review_in.review_comment,
    )
    if not reviewed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="提交记录不存在")
    return TeacherSubmissionDetailRead.model_validate(reviewed)


@router.post("/submissions/batch-review", response_model=TeacherBatchReviewResponse)
def review_teacher_submissions_batch(
    payload: TeacherBatchReviewRequest,
    db: DBSession,
    teacher_user: CurrentTeacher,
) -> TeacherBatchReviewResponse:
    success_submission_ids: list[int] = []
    failed_items: list[dict] = []
    seen_submission_ids: set[int] = set()
    for submission_id in payload.submission_ids:
        if submission_id in seen_submission_ids:
            continue
        seen_submission_ids.add(submission_id)
        reviewed = crud_teacher.review_submission(
            db,
            submission_id=submission_id,
            reviewer_id=teacher_user.id,
            review_status=payload.review_status,
            review_comment=payload.review_comment,
        )
        if not reviewed:
            failed_items.append({"submission_id": submission_id, "reason": "提交记录不存在"})
            continue
        success_submission_ids.append(submission_id)
    return TeacherBatchReviewResponse(
        success_count=len(success_submission_ids),
        failed_count=len(failed_items),
        success_submission_ids=success_submission_ids,
        failed_items=failed_items,
        message="批量批阅完成",
    )


@router.post(
    "/experiments/{experiment_id}/students/{user_id}/return",
    response_model=TeacherReturnResponse,
)
def teacher_return_student_submission(
    experiment_id: int,
    user_id: int,
    db: DBSession,
    teacher_user: CurrentTeacher,
) -> TeacherReturnResponse:
    _ = teacher_user
    _ensure_experiment_exists(db, experiment_id=experiment_id)
    _ensure_user_exists(db, user_id=user_id)
    reopened = crud_teacher.teacher_return_experiment(db, experiment_id=experiment_id, user_id=user_id)
    if not reopened:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="当前用户在该实验下没有可退回的最终提交",
        )
    return TeacherReturnResponse(
        experiment_id=experiment_id,
        user_id=user_id,
        reopened_submission_id=reopened.id,
        reopened_version=reopened.version,
        latest_status=reopened.status,
        message="已退回，当前用户可继续修改并重新提交",
    )


@router.post(
    "/experiments/{experiment_id}/batch-return",
    response_model=TeacherBatchReturnResponse,
)
def teacher_batch_return_student_submission(
    experiment_id: int,
    payload: TeacherBatchReturnRequest,
    db: DBSession,
    teacher_user: CurrentTeacher,
) -> TeacherBatchReturnResponse:
    _ = teacher_user
    _ensure_experiment_exists(db, experiment_id=experiment_id)
    success_user_ids: list[int] = []
    failed_items: list[dict] = []
    seen_user_ids: set[int] = set()
    for user_id in payload.user_ids:
        if user_id in seen_user_ids:
            continue
        seen_user_ids.add(user_id)
        user = crud_user.get_by_id(db, user_id=user_id)
        if not user:
            failed_items.append({"user_id": user_id, "reason": "用户不存在"})
            continue
        reopened = crud_teacher.teacher_return_experiment(db, experiment_id=experiment_id, user_id=user_id)
        if not reopened:
            failed_items.append({"user_id": user_id, "reason": "当前没有可退回的最终提交"})
            continue
        success_user_ids.append(user_id)
    return TeacherBatchReturnResponse(
        success_count=len(success_user_ids),
        failed_count=len(failed_items),
        success_user_ids=success_user_ids,
        failed_items=failed_items,
        message="批量退回完成",
    )


@router.get("/students", response_model=TeacherStudentAccountPage)
def get_teacher_students(
    db: DBSession,
    teacher_user: CurrentTeacher,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    keyword: str = Query(default=""),
    class_name: str = Query(default=""),
    student_no: str = Query(default=""),
    is_enabled: bool | None = Query(default=None),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
) -> TeacherStudentAccountPage:
    _ = teacher_user
    _validate_student_list_sort(sort_by, sort_order)
    data = crud_teacher.list_students(
        db,
        page=page,
        page_size=page_size,
        keyword=keyword,
        class_name=class_name,
        student_no=student_no,
        is_enabled=is_enabled,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return TeacherStudentAccountPage(
        items=[TeacherStudentAccountItem.model_validate(item) for item in data["items"]],
        total=data["total"],
        page=data["page"],
        page_size=data["page_size"],
        total_pages=data["total_pages"],
    )


@router.get("/students/class-options", response_model=list[str])
def get_teacher_student_class_options(
    db: DBSession,
    teacher_user: CurrentTeacher,
) -> list[str]:
    _ = teacher_user
    return crud_teacher.list_student_class_options(db)


@router.get("/students/export")
def export_teacher_students(
    db: DBSession,
    teacher_user: CurrentTeacher,
    keyword: str = Query(default=""),
    class_name: str = Query(default=""),
    student_no: str = Query(default=""),
    is_enabled: bool | None = Query(default=None),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
) -> Response:
    _ = teacher_user
    _validate_student_list_sort(sort_by, sort_order)
    rows = crud_teacher.list_students_for_export(
        db,
        keyword=keyword,
        class_name=class_name,
        student_no=student_no,
        is_enabled=is_enabled,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    file_bytes = build_student_accounts_export_bytes(rows)
    encoded_filename = quote(STUDENT_ACCOUNT_EXPORT_FILENAME)
    headers = {
        "Content-Disposition": (
            f'attachment; filename="student_accounts.xlsx"; '
            f"filename*=UTF-8''{encoded_filename}"
        ),
        "Cache-Control": "no-store",
    }
    return Response(
        content=file_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


@router.post("/students/batch-reset-password", response_model=TeacherStudentBatchPasswordResetResponse)
def batch_reset_teacher_students_password(
    payload: TeacherStudentBatchPasswordResetRequest,
    db: DBSession,
    teacher_user: CurrentTeacher,
) -> TeacherStudentBatchPasswordResetResponse:
    _ = teacher_user
    new_password = payload.new_password.strip()
    if len(new_password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="新密码长度不能少于 6 位")

    success_user_ids: list[int] = []
    failed_items: list[dict] = []
    seen_user_ids: set[int] = set()
    for user_id in payload.user_ids:
        if user_id in seen_user_ids:
            continue
        seen_user_ids.add(user_id)
        user = crud_user.get_by_id(db, user_id=user_id)
        if not user:
            failed_items.append({"user_id": user_id, "reason": "用户不存在"})
            continue
        if user.role != "student":
            failed_items.append({"user_id": user_id, "reason": "仅支持学生账号"})
            continue
        try:
            with db.begin_nested():
                user.password_hash = get_password_hash(new_password)
                user.must_change_password = True
                db.add(user)
            success_user_ids.append(user_id)
        except Exception as exc:
            failed_items.append({"user_id": user_id, "reason": f"重置失败：{exc}"})
    db.commit()
    return TeacherStudentBatchPasswordResetResponse(
        success_count=len(success_user_ids),
        failed_count=len(failed_items),
        success_user_ids=success_user_ids,
        failed_items=failed_items,
        message="批量重置密码完成",
    )


@router.post("/students/{user_id}/enable", response_model=TeacherStudentStatusUpdateResponse)
def enable_teacher_student_account(
    user_id: int,
    db: DBSession,
    teacher_user: CurrentTeacher,
) -> TeacherStudentStatusUpdateResponse:
    _ = teacher_user
    user = crud_user.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    if user.role != "student":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="仅支持学生账号")
    user.is_enabled = True
    db.add(user)
    db.commit()
    db.refresh(user)
    return TeacherStudentStatusUpdateResponse(user_id=user.id, is_enabled=user.is_enabled, message="账号已启用")


@router.post("/students/{user_id}/disable", response_model=TeacherStudentStatusUpdateResponse)
def disable_teacher_student_account(
    user_id: int,
    db: DBSession,
    teacher_user: CurrentTeacher,
) -> TeacherStudentStatusUpdateResponse:
    _ = teacher_user
    user = crud_user.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    if user.role != "student":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="仅支持学生账号")
    user.is_enabled = False
    db.add(user)
    db.commit()
    db.refresh(user)
    return TeacherStudentStatusUpdateResponse(user_id=user.id, is_enabled=user.is_enabled, message="账号已停用")


@router.post("/students/batch-enable", response_model=TeacherStudentBatchStatusUpdateResponse)
def batch_enable_teacher_students(
    payload: TeacherStudentBatchStatusRequest,
    db: DBSession,
    teacher_user: CurrentTeacher,
) -> TeacherStudentBatchStatusUpdateResponse:
    _ = teacher_user
    success_user_ids, failed_items = _batch_update_students_enabled_status(
        db=db,
        user_ids=payload.user_ids,
        target_enabled=True,
    )
    return TeacherStudentBatchStatusUpdateResponse(
        success_count=len(success_user_ids),
        failed_count=len(failed_items),
        success_user_ids=success_user_ids,
        failed_items=failed_items,
        message="批量启用完成",
    )


@router.post("/students/batch-disable", response_model=TeacherStudentBatchStatusUpdateResponse)
def batch_disable_teacher_students(
    payload: TeacherStudentBatchStatusRequest,
    db: DBSession,
    teacher_user: CurrentTeacher,
) -> TeacherStudentBatchStatusUpdateResponse:
    _ = teacher_user
    success_user_ids, failed_items = _batch_update_students_enabled_status(
        db=db,
        user_ids=payload.user_ids,
        target_enabled=False,
    )
    return TeacherStudentBatchStatusUpdateResponse(
        success_count=len(success_user_ids),
        failed_count=len(failed_items),
        success_user_ids=success_user_ids,
        failed_items=failed_items,
        message="批量停用完成",
    )


@router.get("/students/import-template")
def download_student_import_template(teacher_user: CurrentTeacher) -> Response:
    _ = teacher_user
    file_bytes = build_student_import_template_bytes()
    encoded_filename = quote(STUDENT_IMPORT_TEMPLATE_FILENAME)
    headers = {
        "Content-Disposition": (
            f'attachment; filename="student_import_template.xlsx"; '
            f"filename*=UTF-8''{encoded_filename}"
        ),
        "Cache-Control": "no-store",
    }
    return Response(
        content=file_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


@router.post("/students/import", response_model=TeacherStudentImportResponse)
async def import_teacher_students(
    db: DBSession,
    teacher_user: CurrentTeacher,
    file: UploadFile = File(...),
) -> TeacherStudentImportResponse:
    _ = teacher_user
    filename = (file.filename or "").strip()
    if not filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="导入失败：缺少文件名")
    if not filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="导入失败：仅支持 .xlsx 文件")
    file_bytes = await file.read()
    try:
        result = import_students_from_excel(db, file_bytes=file_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"导入失败：{exc}") from exc
    return TeacherStudentImportResponse.model_validate(result)
