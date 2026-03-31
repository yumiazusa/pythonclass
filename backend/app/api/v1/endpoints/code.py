from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentSubmissionUser, DBSession
from app.crud import crud_experiment, crud_submission
from app.schemas.code_run import CodeRunRequest, CodeRunResponse
from app.services.code_runner import run_python_code
from app.services.guided_template import validate_imports_in_code

router = APIRouter(prefix="/code", tags=["code"])


@router.post("/run", response_model=CodeRunResponse)
def run_code(payload: CodeRunRequest, db: DBSession, current_user: CurrentSubmissionUser) -> CodeRunResponse:
    experiment = crud_experiment.get(db, experiment_id=payload.experiment_id)
    if not experiment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="实验不存在")
    if experiment.interaction_mode == "guided_template":
        import_validation = validate_imports_in_code(payload.code)
        if not import_validation.valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="导入库校验失败：" + "；".join(import_validation.errors),
            )
    workspace_status = crud_submission.get_workspace_status(
        db,
        user_id=current_user.id,
        experiment_id=payload.experiment_id,
        user_role=current_user.role,
    )
    if not workspace_status["can_run"]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=workspace_status["message"])
    return run_python_code(payload.code)
