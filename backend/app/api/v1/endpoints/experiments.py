from datetime import datetime, timezone

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


def _normalize_to_utc_naive(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)


def _serialize_class_deadlines(raw_deadlines) -> dict | None:
    if not raw_deadlines:
        return None
    serialized: dict[str, dict[str, str | None]] = {}
    for raw_class_name, raw_schedule in raw_deadlines.items():
        class_name = str(raw_class_name or "").strip()
        if not class_name:
            continue
        schedule = raw_schedule.model_dump() if hasattr(raw_schedule, "model_dump") else dict(raw_schedule or {})
        open_at = _normalize_to_utc_naive(schedule.get("open_at"))
        due_at = _normalize_to_utc_naive(schedule.get("due_at"))
        if open_at and due_at and due_at <= open_at:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{class_name} 的截止时间必须晚于开放时间")
        if not open_at and not due_at:
            continue
        serialized[class_name] = {
            "open_at": open_at.isoformat() if open_at else None,
            "due_at": due_at.isoformat() if due_at else None,
        }
    return serialized or None


def _to_experiment_read(experiment, current_user) -> ExperimentRead:
    class_name = current_user.class_name if current_user.role == "student" else None
    schedule = crud_experiment.resolve_effective_schedule(experiment, class_name=class_name)
    return ExperimentRead.model_validate(experiment).model_copy(
        update={
            "effective_open_at": schedule["open_at"],
            "effective_due_at": schedule["due_at"],
            "schedule_source": schedule["schedule_source"],
        }
    )


@router.post("", response_model=ExperimentRead, status_code=status.HTTP_201_CREATED)
def create_experiment(experiment_in: ExperimentCreate, db: DBSession, teacher_user: CurrentTeacher) -> ExperimentRead:
    _ = teacher_user
    if experiment_in.open_at and experiment_in.due_at and experiment_in.due_at <= experiment_in.open_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="截止时间必须晚于开放时间")
    existing = crud_experiment.get_by_slug(db, slug=experiment_in.slug)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="slug 已存在")

    create_payload = experiment_in.model_dump()
    create_payload["open_at"] = _normalize_to_utc_naive(experiment_in.open_at)
    create_payload["due_at"] = _normalize_to_utc_naive(experiment_in.due_at)
    create_payload["class_deadlines"] = _serialize_class_deadlines(experiment_in.class_deadlines)
    experiment = crud_experiment.create_admin_experiment(db, create_payload)
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
    return [_to_experiment_read(item, current_user) for item in experiments]


@router.get("/{experiment_id}", response_model=ExperimentRead)
def get_experiment(experiment_id: int, db: DBSession, current_user: CurrentUser) -> ExperimentRead:
    experiment = crud_experiment.get(db, experiment_id=experiment_id)
    if not experiment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="实验不存在")
    if not experiment.is_active and current_user.role not in {"teacher", "admin"}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="实验不存在")
    if current_user.role not in {"teacher", "admin"} and not experiment.is_published:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="实验不存在")
    return _to_experiment_read(experiment, current_user)


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
