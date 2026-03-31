from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentSubmissionUser, DBSession
from app.crud import crud_experiment, crud_submission
from app.schemas.submission import (
    CodeSubmissionCreate,
    CodeSubmissionHistoryItem,
    CodeSubmissionRead,
    WorkspaceStatusRead,
)

router = APIRouter(prefix="/submissions", tags=["submissions"])


def _ensure_experiment_exists(db: DBSession, experiment_id: int) -> None:
    experiment = crud_experiment.get(db, experiment_id=experiment_id)
    if not experiment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="实验不存在")


@router.post("/save", response_model=CodeSubmissionRead, status_code=status.HTTP_201_CREATED)
def save_submission(submission_in: CodeSubmissionCreate, db: DBSession, current_user: CurrentSubmissionUser) -> CodeSubmissionRead:
    if current_user.role == "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="管理员测试模式不支持保存草稿")
    _ensure_experiment_exists(db, experiment_id=submission_in.experiment_id)
    workspace_status = crud_submission.get_workspace_status(
        db,
        user_id=current_user.id,
        experiment_id=submission_in.experiment_id,
        user_role=current_user.role,
    )
    if workspace_status["is_locked"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="该实验已提交最终版，不能再保存草稿",
        )
    if not workspace_status["can_save_draft"]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=workspace_status["message"])
    submission = crud_submission.create(
        db,
        user_id=current_user.id,
        submission_in=submission_in,
        status="draft",
    )
    return CodeSubmissionRead.model_validate(submission)


@router.post("/submit", response_model=CodeSubmissionRead, status_code=status.HTTP_201_CREATED)
def submit_submission(
    submission_in: CodeSubmissionCreate, db: DBSession, current_user: CurrentSubmissionUser
) -> CodeSubmissionRead:
    if current_user.role == "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="管理员测试模式不支持正式提交")
    _ensure_experiment_exists(db, experiment_id=submission_in.experiment_id)
    workspace_status = crud_submission.get_workspace_status(
        db,
        user_id=current_user.id,
        experiment_id=submission_in.experiment_id,
        user_role=current_user.role,
    )
    if workspace_status["is_locked"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="该实验已提交最终版，如需修改请先撤回提交或等待教师退回",
        )
    if not workspace_status["can_submit"]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=workspace_status["message"])
    submission = crud_submission.create(
        db,
        user_id=current_user.id,
        submission_in=submission_in,
        status="submitted",
    )
    return CodeSubmissionRead.model_validate(submission)


@router.get("/latest/{experiment_id}", response_model=CodeSubmissionRead)
def get_latest_submission(experiment_id: int, db: DBSession, current_user: CurrentSubmissionUser) -> CodeSubmissionRead:
    _ensure_experiment_exists(db, experiment_id=experiment_id)
    submission = crud_submission.get_latest(db, user_id=current_user.id, experiment_id=experiment_id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="暂无提交记录")
    return CodeSubmissionRead.model_validate(submission)


@router.get("/history/{experiment_id}", response_model=list[CodeSubmissionHistoryItem])
def get_submission_history(
    experiment_id: int,
    db: DBSession,
    current_user: CurrentSubmissionUser,
) -> list[CodeSubmissionHistoryItem]:
    _ensure_experiment_exists(db, experiment_id=experiment_id)
    history = crud_submission.list_history(db, user_id=current_user.id, experiment_id=experiment_id)
    return [CodeSubmissionHistoryItem.model_validate(item) for item in history]


@router.get("/workspace-status/{experiment_id}", response_model=WorkspaceStatusRead)
def get_workspace_status(experiment_id: int, db: DBSession, current_user: CurrentSubmissionUser) -> WorkspaceStatusRead:
    _ensure_experiment_exists(db, experiment_id=experiment_id)
    status_payload = crud_submission.get_workspace_status(
        db,
        user_id=current_user.id,
        experiment_id=experiment_id,
        user_role=current_user.role,
    )
    return WorkspaceStatusRead.model_validate(status_payload)


@router.get("/{submission_id}", response_model=CodeSubmissionRead)
def get_submission(submission_id: int, db: DBSession, current_user: CurrentSubmissionUser) -> CodeSubmissionRead:
    submission = crud_submission.get(db, submission_id=submission_id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="提交记录不存在")
    if submission.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问该提交记录")
    return CodeSubmissionRead.model_validate(submission)
