from datetime import datetime, timezone
from math import ceil

from sqlalchemy import case, func, literal, or_, select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.code_submission import CodeSubmission
from app.models.experiment import Experiment
from app.models.user import User


def _latest_submissions_subquery():
    latest_version_subquery = (
        select(
            CodeSubmission.user_id.label("user_id"),
            CodeSubmission.experiment_id.label("experiment_id"),
            func.max(CodeSubmission.version).label("latest_version"),
        )
        .group_by(CodeSubmission.user_id, CodeSubmission.experiment_id)
        .subquery()
    )
    return (
        select(
            CodeSubmission.id.label("submission_id"),
            CodeSubmission.user_id.label("user_id"),
            CodeSubmission.experiment_id.label("experiment_id"),
            CodeSubmission.version.label("version"),
            CodeSubmission.status.label("status"),
            CodeSubmission.updated_at.label("updated_at"),
            CodeSubmission.code.label("code"),
            CodeSubmission.run_output.label("run_output"),
            CodeSubmission.is_passed.label("is_passed"),
            CodeSubmission.review_status.label("review_status"),
            CodeSubmission.review_comment.label("review_comment"),
            CodeSubmission.reviewed_by.label("reviewed_by"),
            CodeSubmission.reviewed_at.label("reviewed_at"),
            CodeSubmission.created_at.label("created_at"),
        )
        .join(
            latest_version_subquery,
            (CodeSubmission.user_id == latest_version_subquery.c.user_id)
            & (CodeSubmission.experiment_id == latest_version_subquery.c.experiment_id)
            & (CodeSubmission.version == latest_version_subquery.c.latest_version),
        )
        .subquery()
    )


def list_experiment_overview(db: Session) -> list[dict]:
    latest_subquery = _latest_submissions_subquery()
    latest_final_version_subquery = (
        select(
            CodeSubmission.user_id.label("user_id"),
            CodeSubmission.experiment_id.label("experiment_id"),
            func.max(CodeSubmission.version).label("latest_final_version"),
        )
        .where(CodeSubmission.status == "submitted")
        .group_by(CodeSubmission.user_id, CodeSubmission.experiment_id)
        .subquery()
    )
    latest_final_subquery = (
        select(
            CodeSubmission.user_id.label("user_id"),
            CodeSubmission.experiment_id.label("experiment_id"),
            CodeSubmission.review_status.label("review_status"),
        )
        .join(
            latest_final_version_subquery,
            (CodeSubmission.user_id == latest_final_version_subquery.c.user_id)
            & (CodeSubmission.experiment_id == latest_final_version_subquery.c.experiment_id)
            & (CodeSubmission.version == latest_final_version_subquery.c.latest_final_version),
        )
        .subquery()
    )
    review_stats_subquery = (
        select(
            latest_final_subquery.c.experiment_id.label("experiment_id"),
            func.sum(case((latest_final_subquery.c.review_status.in_(["passed", "failed"]), 1), else_=0)).label(
                "reviewed_count"
            ),
            func.sum(case((latest_final_subquery.c.review_status == "passed", 1), else_=0)).label("passed_count"),
            func.sum(case((latest_final_subquery.c.review_status == "failed", 1), else_=0)).label("failed_count"),
            func.sum(
                case(
                    (
                        (latest_final_subquery.c.review_status == "pending")
                        | (latest_final_subquery.c.review_status.is_(None)),
                        1,
                    ),
                    else_=0,
                )
            ).label("pending_review_count"),
        )
        .group_by(latest_final_subquery.c.experiment_id)
        .subquery()
    )
    statement = (
        select(
            Experiment.id.label("experiment_id"),
            Experiment.title.label("title"),
            Experiment.is_published.label("is_published"),
            Experiment.open_at.label("open_at"),
            Experiment.due_at.label("due_at"),
            func.count(latest_subquery.c.user_id).label("total_students_with_records"),
            func.sum(case((latest_subquery.c.status == "submitted", 1), else_=0)).label("submitted_count"),
            func.sum(case((latest_subquery.c.status == "draft", 1), else_=0)).label("draft_count"),
            func.sum(case((latest_subquery.c.status == "submitted", 1), else_=0)).label("locked_count"),
            func.max(review_stats_subquery.c.reviewed_count).label("reviewed_count"),
            func.max(review_stats_subquery.c.passed_count).label("passed_count"),
            func.max(review_stats_subquery.c.failed_count).label("failed_count"),
            func.max(review_stats_subquery.c.pending_review_count).label("pending_review_count"),
            func.max(latest_subquery.c.updated_at).label("updated_at"),
        )
        .select_from(Experiment)
        .outerjoin(latest_subquery, latest_subquery.c.experiment_id == Experiment.id)
        .outerjoin(review_stats_subquery, review_stats_subquery.c.experiment_id == Experiment.id)
        .group_by(
            Experiment.id,
            Experiment.title,
            Experiment.is_published,
            Experiment.open_at,
            Experiment.due_at,
        )
        .order_by(Experiment.id.desc())
    )
    rows = db.execute(statement).all()
    return [
        {
            "experiment_id": row.experiment_id,
            "title": row.title,
            "is_published": bool(row.is_published),
            "open_at": row.open_at,
            "due_at": row.due_at,
            "total_students_with_records": row.total_students_with_records or 0,
            "submitted_count": row.submitted_count or 0,
            "draft_count": row.draft_count or 0,
            "locked_count": row.locked_count or 0,
            "reviewed_count": row.reviewed_count or 0,
            "passed_count": row.passed_count or 0,
            "failed_count": row.failed_count or 0,
            "pending_review_count": row.pending_review_count or 0,
            "updated_at": row.updated_at,
        }
        for row in rows
    ]


def _build_experiment_student_latest_status_statement(
    *,
    experiment_id: int,
    keyword: str = "",
    status_filter: str = "all",
    class_name: str = "",
    student_no: str = "",
    review_status_filter: str = "all",
    sort_by: str = "latest_updated_at",
    sort_order: str = "desc",
):
    latest_subquery = _latest_submissions_subquery()

    student_no_column = getattr(User, "student_no", None)
    class_name_column = getattr(User, "class_name", None)
    full_name_column = getattr(User, "full_name", None)
    selected_student_no = student_no_column if student_no_column is not None else literal(None)
    selected_class_name = class_name_column if class_name_column is not None else literal(None)
    selected_full_name = full_name_column if full_name_column is not None else literal(None)

    statement = (
        select(
            latest_subquery.c.user_id,
            User.username,
            selected_full_name.label("full_name"),
            selected_student_no.label("student_no"),
            selected_class_name.label("class_name"),
            latest_subquery.c.submission_id.label("latest_submission_id"),
            latest_subquery.c.version.label("latest_version"),
            latest_subquery.c.status.label("latest_status"),
            latest_subquery.c.review_status.label("review_status"),
            latest_subquery.c.reviewed_at.label("reviewed_at"),
            latest_subquery.c.updated_at.label("latest_updated_at"),
        )
        .join(User, User.id == latest_subquery.c.user_id)
        .where(latest_subquery.c.experiment_id == experiment_id)
    )

    clean_keyword = keyword.strip()
    if clean_keyword:
        keyword_conditions = [User.username.ilike(f"%{clean_keyword}%")]
        if full_name_column is not None:
            keyword_conditions.append(full_name_column.ilike(f"%{clean_keyword}%"))
        if student_no_column is not None:
            keyword_conditions.append(student_no_column.ilike(f"%{clean_keyword}%"))
        statement = statement.where(or_(*keyword_conditions))

    if status_filter in {"draft", "submitted"}:
        statement = statement.where(latest_subquery.c.status == status_filter)

    if review_status_filter in {"pending", "passed", "failed"}:
        statement = statement.where(latest_subquery.c.review_status == review_status_filter)

    clean_class_name = class_name.strip()
    if clean_class_name and class_name_column is not None:
        statement = statement.where(class_name_column.ilike(f"%{clean_class_name}%"))

    clean_student_no = student_no.strip()
    if clean_student_no and student_no_column is not None:
        statement = statement.where(student_no_column.ilike(f"%{clean_student_no}%"))

    sort_mapping = {
        "latest_updated_at": latest_subquery.c.updated_at,
        "username": User.username,
        "latest_version": latest_subquery.c.version,
    }
    sort_column = sort_mapping.get(sort_by, latest_subquery.c.updated_at)
    if sort_order == "asc":
        statement = statement.order_by(sort_column.asc(), latest_subquery.c.user_id.asc())
    else:
        statement = statement.order_by(sort_column.desc(), latest_subquery.c.user_id.asc())

    return statement


def _map_experiment_student_latest_status_rows(rows) -> list[dict]:
    return [
        {
            "user_id": row.user_id,
            "username": row.username,
            "full_name": row.full_name,
            "student_no": row.student_no,
            "class_name": row.class_name,
            "latest_submission_id": row.latest_submission_id,
            "latest_version": row.latest_version,
            "latest_status": row.latest_status,
            "is_locked": row.latest_status == "submitted",
            "review_status": row.review_status or "pending",
            "reviewed_at": row.reviewed_at,
            "needs_review": row.latest_status == "submitted" and (row.review_status or "pending") == "pending",
            "latest_updated_at": row.latest_updated_at,
            "can_reopen": row.latest_status == "submitted",
            "has_final_submission": row.latest_status == "submitted",
        }
        for row in rows
    ]


def list_experiment_student_latest_status(
    db: Session,
    experiment_id: int,
    page: int = 1,
    page_size: int = 10,
    keyword: str = "",
    status_filter: str = "all",
    class_name: str = "",
    student_no: str = "",
    review_status_filter: str = "all",
    sort_by: str = "latest_updated_at",
    sort_order: str = "desc",
) -> dict:
    statement = _build_experiment_student_latest_status_statement(
        experiment_id=experiment_id,
        keyword=keyword,
        status_filter=status_filter,
        class_name=class_name,
        student_no=student_no,
        review_status_filter=review_status_filter,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    total_statement = select(func.count()).select_from(statement.subquery())
    total = db.execute(total_statement).scalar_one() or 0
    total_pages = ceil(total / page_size) if total > 0 else 0
    offset = (page - 1) * page_size
    rows = db.execute(statement.offset(offset).limit(page_size)).all()
    items = _map_experiment_student_latest_status_rows(rows)
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


def list_experiment_student_latest_status_for_export(
    db: Session,
    *,
    experiment_id: int,
    keyword: str = "",
    status_filter: str = "all",
    class_name: str = "",
    student_no: str = "",
    review_status_filter: str = "all",
    sort_by: str = "latest_updated_at",
    sort_order: str = "desc",
) -> list[dict]:
    statement = _build_experiment_student_latest_status_statement(
        experiment_id=experiment_id,
        keyword=keyword,
        status_filter=status_filter,
        class_name=class_name,
        student_no=student_no,
        review_status_filter=review_status_filter,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    rows = db.execute(statement).all()
    return _map_experiment_student_latest_status_rows(rows)


def get_experiment_class_summary(db: Session, *, experiment_id: int) -> list[dict]:
    latest_subquery = _latest_submissions_subquery()
    class_name_expr = func.coalesce(func.nullif(User.class_name, ""), "未分班")
    statement = (
        select(
            class_name_expr.label("class_name"),
            func.count(User.id).label("total_students"),
            func.sum(case((latest_subquery.c.status == "submitted", 1), else_=0)).label("submitted_count"),
            func.sum(
                case(
                    (
                        (latest_subquery.c.status == "submitted") & (latest_subquery.c.review_status == "passed"),
                        1,
                    ),
                    else_=0,
                )
            ).label("passed_count"),
            func.sum(
                case(
                    (
                        (latest_subquery.c.status == "submitted") & (latest_subquery.c.review_status == "failed"),
                        1,
                    ),
                    else_=0,
                )
            ).label("failed_count"),
            func.sum(
                case(
                    (
                        (latest_subquery.c.status == "submitted")
                        & ((latest_subquery.c.review_status == "pending") | latest_subquery.c.review_status.is_(None)),
                        1,
                    ),
                    else_=0,
                )
            ).label("pending_review_count"),
        )
        .select_from(User)
        .outerjoin(
            latest_subquery,
            (latest_subquery.c.user_id == User.id) & (latest_subquery.c.experiment_id == experiment_id),
        )
        .where(User.role == "student")
        .group_by(class_name_expr)
        .order_by(class_name_expr.asc())
    )
    rows = db.execute(statement).all()
    items: list[dict] = []
    for row in rows:
        total_students = int(row.total_students or 0)
        submitted_count = int(row.submitted_count or 0)
        passed_count = int(row.passed_count or 0)
        failed_count = int(row.failed_count or 0)
        pending_review_count = int(row.pending_review_count or 0)
        not_submitted_count = total_students - submitted_count
        items.append(
            {
                "class_name": row.class_name or "未分班",
                "total_students": total_students,
                "submitted_count": submitted_count,
                "passed_count": passed_count,
                "failed_count": failed_count,
                "pending_review_count": pending_review_count,
                "not_submitted_count": not_submitted_count if not_submitted_count > 0 else 0,
            }
        )
    return items


def list_student_history_by_experiment(db: Session, experiment_id: int, user_id: int) -> list[CodeSubmission]:
    statement = (
        select(CodeSubmission)
        .where(
            CodeSubmission.experiment_id == experiment_id,
            CodeSubmission.user_id == user_id,
        )
        .order_by(CodeSubmission.version.desc())
    )
    return list(db.execute(statement).scalars().all())


def get_submission_detail(db: Session, submission_id: int) -> CodeSubmission | None:
    return db.get(CodeSubmission, submission_id)


def review_submission(
    db: Session,
    submission_id: int,
    reviewer_id: int,
    review_status: str,
    review_comment: str | None,
) -> CodeSubmission | None:
    submission = db.get(CodeSubmission, submission_id)
    if not submission:
        return None
    cleaned_comment = review_comment.strip() if isinstance(review_comment, str) else None
    submission.review_status = review_status
    submission.review_comment = cleaned_comment or None
    submission.reviewed_by = reviewer_id
    submission.reviewed_at = datetime.now(timezone.utc)
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


def teacher_return_experiment(db: Session, experiment_id: int, user_id: int) -> CodeSubmission | None:
    latest_statement = (
        select(CodeSubmission)
        .where(
            CodeSubmission.user_id == user_id,
            CodeSubmission.experiment_id == experiment_id,
        )
        .order_by(CodeSubmission.version.desc())
        .limit(1)
    )
    latest = db.execute(latest_statement).scalar_one_or_none()
    if not latest or latest.status != "submitted":
        return None

    reopened = CodeSubmission(
        user_id=user_id,
        experiment_id=experiment_id,
        code=latest.code,
        status="draft",
        run_output=latest.run_output,
        is_passed=latest.is_passed,
        review_status="pending",
        review_comment=None,
        reviewed_by=None,
        reviewed_at=None,
        version=latest.version + 1,
    )
    db.add(reopened)
    db.commit()
    db.refresh(reopened)
    return reopened


def _build_student_accounts_statement(
    *,
    keyword: str = "",
    class_name: str = "",
    student_no: str = "",
    is_enabled: bool | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
):
    statement = (
        select(
            User.id.label("user_id"),
            User.username.label("username"),
            User.full_name.label("full_name"),
            User.student_no.label("student_no"),
            User.class_name.label("class_name"),
            User.role.label("role"),
            User.is_enabled.label("is_enabled"),
            User.created_at.label("created_at"),
        )
        .where(User.role == "student")
    )

    clean_keyword = keyword.strip()
    if clean_keyword:
        statement = statement.where(
            or_(
                User.username.ilike(f"%{clean_keyword}%"),
                User.full_name.ilike(f"%{clean_keyword}%"),
                User.student_no.ilike(f"%{clean_keyword}%"),
            )
        )

    clean_class_name = class_name.strip()
    if clean_class_name:
        statement = statement.where(User.class_name.ilike(f"%{clean_class_name}%"))

    clean_student_no = student_no.strip()
    if clean_student_no:
        statement = statement.where(User.student_no.ilike(f"%{clean_student_no}%"))

    if is_enabled is not None:
        statement = statement.where(User.is_enabled == is_enabled)

    sort_mapping = {
        "created_at": User.created_at,
        "username": User.username,
        "full_name": User.full_name,
        "student_no": User.student_no,
        "class_name": User.class_name,
        "is_enabled": User.is_enabled,
    }
    sort_column = sort_mapping.get(sort_by, User.created_at)
    if sort_order == "asc":
        statement = statement.order_by(sort_column.asc(), User.id.asc())
    else:
        statement = statement.order_by(sort_column.desc(), User.id.asc())
    return statement


def list_students(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 10,
    keyword: str = "",
    class_name: str = "",
    student_no: str = "",
    is_enabled: bool | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> dict:
    statement = _build_student_accounts_statement(
        keyword=keyword,
        class_name=class_name,
        student_no=student_no,
        is_enabled=is_enabled,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    total_statement = select(func.count()).select_from(statement.subquery())
    total = db.execute(total_statement).scalar_one() or 0
    total_pages = ceil(total / page_size) if total > 0 else 0
    offset = (page - 1) * page_size
    rows = db.execute(statement.offset(offset).limit(page_size)).all()
    items = [
        {
            "user_id": row.user_id,
            "username": row.username,
            "full_name": row.full_name,
            "student_no": row.student_no,
            "class_name": row.class_name,
            "role": row.role,
            "is_enabled": bool(row.is_enabled),
            "created_at": row.created_at,
        }
        for row in rows
    ]
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


def list_students_for_export(
    db: Session,
    *,
    keyword: str = "",
    class_name: str = "",
    student_no: str = "",
    is_enabled: bool | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> list[dict]:
    statement = _build_student_accounts_statement(
        keyword=keyword,
        class_name=class_name,
        student_no=student_no,
        is_enabled=is_enabled,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    rows = db.execute(statement).all()
    return [
        {
            "user_id": row.user_id,
            "username": row.username,
            "full_name": row.full_name,
            "student_no": row.student_no,
            "class_name": row.class_name,
            "role": row.role,
            "is_enabled": bool(row.is_enabled),
            "created_at": row.created_at,
        }
        for row in rows
    ]


def list_student_class_options(db: Session) -> list[str]:
    statement = (
        select(User.class_name)
        .where(
            User.role == "student",
            User.class_name.is_not(None),
            User.class_name != "",
        )
        .group_by(User.class_name)
        .order_by(User.class_name.asc())
    )
    rows = db.execute(statement).scalars().all()
    return [item for item in rows if isinstance(item, str) and item.strip()]


def update_student_enabled_status(db: Session, *, user_id: int, is_enabled: bool) -> User | None:
    user = db.get(User, user_id)
    if not user or user.role != "student":
        return None
    user.is_enabled = is_enabled
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def reset_student_password(db: Session, *, user_id: int, new_password: str) -> User | None:
    user = db.get(User, user_id)
    if not user or user.role != "student":
        return None
    user.password_hash = get_password_hash(new_password)
    user.must_change_password = True
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
