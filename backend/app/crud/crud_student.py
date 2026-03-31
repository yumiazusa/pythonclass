from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models.code_submission import CodeSubmission
from app.models.experiment import Experiment
from app.models.user import User


def _latest_user_submissions_subquery(*, user_id: int):
    latest_version_subquery = (
        select(
            CodeSubmission.experiment_id.label("experiment_id"),
            func.max(CodeSubmission.version).label("latest_version"),
        )
        .where(CodeSubmission.user_id == user_id)
        .group_by(CodeSubmission.experiment_id)
        .subquery()
    )
    return (
        select(
            CodeSubmission.id.label("submission_id"),
            CodeSubmission.experiment_id.label("experiment_id"),
            CodeSubmission.status.label("latest_status"),
            CodeSubmission.review_status.label("review_status"),
            CodeSubmission.updated_at.label("latest_updated_at"),
        )
        .join(
            latest_version_subquery,
            (CodeSubmission.experiment_id == latest_version_subquery.c.experiment_id)
            & (CodeSubmission.version == latest_version_subquery.c.latest_version),
        )
        .where(CodeSubmission.user_id == user_id)
        .subquery()
    )


def get_dashboard_payload(db: Session, *, user_id: int) -> dict | None:
    user = db.get(User, user_id)
    if not user:
        return None

    visible_experiments_subquery = (
        select(
            Experiment.id.label("experiment_id"),
            Experiment.title.label("title"),
            Experiment.interaction_mode.label("interaction_mode"),
        )
        .where(
            Experiment.is_active.is_(True),
            Experiment.is_published.is_(True),
        )
        .subquery()
    )
    latest_user_subquery = _latest_user_submissions_subquery(user_id=user_id)

    summary_statement = (
        select(
            func.count(visible_experiments_subquery.c.experiment_id).label("total_experiments"),
            func.sum(case((latest_user_subquery.c.latest_status == "submitted", 1), else_=0)).label("submitted_count"),
            func.sum(
                case(
                    (
                        (latest_user_subquery.c.latest_status == "submitted")
                        & (latest_user_subquery.c.review_status == "passed"),
                        1,
                    ),
                    else_=0,
                )
            ).label("passed_count"),
            func.sum(
                case(
                    (
                        (latest_user_subquery.c.latest_status == "submitted")
                        & (latest_user_subquery.c.review_status == "failed"),
                        1,
                    ),
                    else_=0,
                )
            ).label("failed_count"),
            func.sum(
                case(
                    (
                        (latest_user_subquery.c.latest_status == "submitted")
                        & (
                            (latest_user_subquery.c.review_status == "pending")
                            | latest_user_subquery.c.review_status.is_(None)
                        ),
                        1,
                    ),
                    else_=0,
                )
            ).label("pending_count"),
            func.sum(case((latest_user_subquery.c.submission_id.is_(None), 1), else_=0)).label("not_started_count"),
        )
        .select_from(visible_experiments_subquery)
        .outerjoin(
            latest_user_subquery,
            latest_user_subquery.c.experiment_id == visible_experiments_subquery.c.experiment_id,
        )
    )
    summary_row = db.execute(summary_statement).one()

    recent_statement = (
        select(
            visible_experiments_subquery.c.experiment_id,
            visible_experiments_subquery.c.title,
            visible_experiments_subquery.c.interaction_mode,
            latest_user_subquery.c.latest_status,
            latest_user_subquery.c.review_status,
            latest_user_subquery.c.latest_updated_at,
        )
        .select_from(latest_user_subquery)
        .join(
            visible_experiments_subquery,
            visible_experiments_subquery.c.experiment_id == latest_user_subquery.c.experiment_id,
        )
        .order_by(latest_user_subquery.c.latest_updated_at.desc(), latest_user_subquery.c.experiment_id.asc())
        .limit(5)
    )
    recent_rows = db.execute(recent_statement).all()

    return {
        "profile": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "student_no": user.student_no,
            "class_name": user.class_name,
            "role": user.role,
        },
        "summary": {
            "total_experiments": int(summary_row.total_experiments or 0),
            "submitted_count": int(summary_row.submitted_count or 0),
            "passed_count": int(summary_row.passed_count or 0),
            "failed_count": int(summary_row.failed_count or 0),
            "pending_count": int(summary_row.pending_count or 0),
            "not_started_count": int(summary_row.not_started_count or 0),
        },
        "recent_items": [
            {
                "experiment_id": row.experiment_id,
                "title": row.title,
                "interaction_mode": row.interaction_mode,
                "latest_status": row.latest_status,
                "review_status": row.review_status or "pending",
                "latest_updated_at": row.latest_updated_at,
            }
            for row in recent_rows
        ],
    }
