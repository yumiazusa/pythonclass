from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentTeacher, CurrentUser, DBSession
from app.crud import crud_experiment
from app.schemas.experiment import (
    ExperimentCreate,
    ExperimentRead,
    GuidedImportValidateRequest,
    GuidedImportValidateResponse,
)
from app.services.guided_template import validate_custom_import_text

router = APIRouter(prefix="/experiments", tags=["experiments"])


@router.post("", response_model=ExperimentRead, status_code=status.HTTP_201_CREATED)
def create_experiment(experiment_in: ExperimentCreate, db: DBSession, teacher_user: CurrentTeacher) -> ExperimentRead:
    _ = teacher_user
    if experiment_in.open_at and experiment_in.due_at and experiment_in.due_at <= experiment_in.open_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="截止时间必须晚于开放时间")
    existing = crud_experiment.get_by_slug(db, slug=experiment_in.slug)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="slug 已存在")

    experiment = crud_experiment.create(db, experiment_in=experiment_in)
    return ExperimentRead.model_validate(experiment)


@router.get("", response_model=list[ExperimentRead])
def list_experiments(
    db: DBSession,
    current_user: CurrentUser,
    include_inactive: bool = Query(default=False),
) -> list[ExperimentRead]:
    can_include_inactive = include_inactive and current_user.role in {"teacher", "admin"}
    experiments = crud_experiment.list_experiments(
        db,
        include_inactive=can_include_inactive,
        viewer_role=current_user.role,
    )
    return [ExperimentRead.model_validate(item) for item in experiments]


@router.get("/{experiment_id}", response_model=ExperimentRead)
def get_experiment(experiment_id: int, db: DBSession, current_user: CurrentUser) -> ExperimentRead:
    experiment = crud_experiment.get(db, experiment_id=experiment_id)
    if not experiment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="实验不存在")
    if not experiment.is_active and current_user.role not in {"teacher", "admin"}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="实验不存在")
    if current_user.role not in {"teacher", "admin"} and not experiment.is_published:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="实验不存在")
    return ExperimentRead.model_validate(experiment)


@router.post("/guided-template/validate-imports", response_model=GuidedImportValidateResponse)
def validate_guided_template_imports(
    payload: GuidedImportValidateRequest,
    current_user: CurrentUser,
) -> GuidedImportValidateResponse:
    _ = current_user
    result = validate_custom_import_text(payload.custom_import_text)
    return GuidedImportValidateResponse(
        valid=result.valid,
        normalized_imports=result.normalized_imports,
        errors=result.errors,
    )
