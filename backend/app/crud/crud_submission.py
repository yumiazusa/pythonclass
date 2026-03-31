from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.crud import crud_experiment
from app.models.code_submission import CodeSubmission
from app.models.experiment import Experiment
from app.schemas.submission import CodeSubmissionCreate


def _next_version(db: Session, user_id: int, experiment_id: int) -> int:
    statement = select(func.max(CodeSubmission.version)).where(
        CodeSubmission.user_id == user_id,
        CodeSubmission.experiment_id == experiment_id,
    )
    current_max = db.execute(statement).scalar_one_or_none()
    if current_max is None:
        return 1
    return current_max + 1


def create(db: Session, user_id: int, submission_in: CodeSubmissionCreate, status: str) -> CodeSubmission:
    version = _next_version(db, user_id=user_id, experiment_id=submission_in.experiment_id)
    submission = CodeSubmission(
        user_id=user_id,
        experiment_id=submission_in.experiment_id,
        code=submission_in.code,
        status=status,
        run_output=submission_in.run_output,
        is_passed=submission_in.is_passed,
        review_status="pending",
        review_comment=None,
        reviewed_by=None,
        reviewed_at=None,
        version=version,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


def get(db: Session, submission_id: int) -> CodeSubmission | None:
    return db.get(CodeSubmission, submission_id)


def get_latest(db: Session, user_id: int, experiment_id: int) -> CodeSubmission | None:
    statement = (
        select(CodeSubmission)
        .where(
            CodeSubmission.user_id == user_id,
            CodeSubmission.experiment_id == experiment_id,
        )
        .order_by(CodeSubmission.version.desc())
        .limit(1)
    )
    return db.execute(statement).scalar_one_or_none()


def list_history(db: Session, user_id: int, experiment_id: int) -> list[CodeSubmission]:
    statement = (
        select(CodeSubmission)
        .where(
            CodeSubmission.user_id == user_id,
            CodeSubmission.experiment_id == experiment_id,
        )
        .order_by(CodeSubmission.version.desc())
    )
    return list(db.execute(statement).scalars().all())


def is_experiment_locked(db: Session, user_id: int, experiment_id: int) -> bool:
    latest = get_latest(db, user_id=user_id, experiment_id=experiment_id)
    if not latest:
        return False
    return latest.status == "submitted"


def get_workspace_status(db: Session, user_id: int, experiment_id: int, user_role: str) -> dict:
    latest = get_latest(db, user_id=user_id, experiment_id=experiment_id)
    experiment = db.get(Experiment, experiment_id)
    runtime_state = (
        crud_experiment.get_experiment_runtime_state(experiment)
        if experiment
        else {"is_published": False, "is_open": False, "is_overdue": False}
    )
    is_locked = bool(latest and latest.status == "submitted")
    if user_role == "admin":
        is_locked = False
    can_edit = True
    can_run = True
    can_save_draft = True
    can_submit = True
    message = "当前可继续编辑和保存草稿"
    if user_role == "admin":
        can_save_draft = False
        can_submit = False
        message = "管理员测试模式：可运行与查看，不支持保存草稿和正式提交"
    if user_role == "student":
        if not runtime_state["is_published"]:
            can_edit = False
            can_run = False
            can_save_draft = False
            can_submit = False
            message = "本实验暂未发布"
        elif not runtime_state["is_open"]:
            can_edit = False
            can_run = False
            can_save_draft = False
            can_submit = False
            message = "本实验尚未开放"
        elif runtime_state["is_overdue"]:
            can_edit = False
            can_run = False
            can_save_draft = False
            can_submit = False
            message = "本实验已截止，当前仅可查看内容"
    if is_locked:
        can_edit = False
        can_run = False
        can_save_draft = False
        can_submit = False
        message = "该实验已提交最终版，当前不可修改"
    return {
        "experiment_id": experiment_id,
        "is_locked": is_locked,
        "latest_submission_id": latest.id if latest else None,
        "latest_version": latest.version if latest else None,
        "latest_status": latest.status if latest else None,
        "is_published": runtime_state["is_published"],
        "is_open": runtime_state["is_open"],
        "is_overdue": runtime_state["is_overdue"],
        "can_edit": can_edit,
        "can_run": can_run,
        "can_save_draft": can_save_draft,
        "can_submit": can_submit,
        "message": message,
    }
