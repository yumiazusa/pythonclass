from datetime import datetime, timezone
from math import ceil

from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session

from app.models.experiment import Experiment
from app.schemas.experiment import ExperimentCreate, ExperimentSettingsUpdate


def create(db: Session, experiment_in: ExperimentCreate) -> Experiment:
    experiment = Experiment(**experiment_in.model_dump())
    db.add(experiment)
    db.commit()
    db.refresh(experiment)
    return experiment


def get(db: Session, experiment_id: int) -> Experiment | None:
    return db.get(Experiment, experiment_id)


def get_by_slug(db: Session, slug: str) -> Experiment | None:
    statement = select(Experiment).where(Experiment.slug == slug)
    return db.execute(statement).scalar_one_or_none()


def get_by_slug_excluding_id(db: Session, *, slug: str, exclude_id: int) -> Experiment | None:
    statement = select(Experiment).where(Experiment.slug == slug, Experiment.id != exclude_id)
    return db.execute(statement).scalar_one_or_none()


def _normalize_datetime(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)


def get_experiment_runtime_state(experiment: Experiment) -> dict:
    now = datetime.utcnow()
    open_at = _normalize_datetime(experiment.open_at)
    due_at = _normalize_datetime(experiment.due_at)
    is_published = bool(experiment.is_published)
    is_open = bool(is_published and (open_at is None or now >= open_at))
    is_overdue = bool(due_at is not None and now > due_at)
    status_text = "进行中"
    if not is_published:
        status_text = "未发布"
    elif not is_open:
        status_text = "尚未开放"
    elif is_overdue:
        status_text = "已截止"
    return {
        "is_published": is_published,
        "is_open": is_open,
        "is_overdue": is_overdue,
        "status_text": status_text,
    }


def list_experiments(db: Session, include_inactive: bool = False, viewer_role: str = "student") -> list[Experiment]:
    statement = select(Experiment)
    if not include_inactive:
        statement = statement.where(Experiment.is_active.is_(True))
    if viewer_role not in {"teacher", "admin"}:
        statement = statement.where(Experiment.is_published.is_(True))
    statement = statement.order_by(
        case((Experiment.sort_order.is_(None), 1), else_=0).asc(),
        Experiment.sort_order.asc(),
        Experiment.id.asc(),
    )
    return list(db.execute(statement).scalars().all())


def _sort_field(sort_by: str):
    if sort_by == "title":
        return Experiment.title
    if sort_by == "slug":
        return Experiment.slug
    if sort_by == "sort_order":
        return Experiment.sort_order
    if sort_by == "open_at":
        return Experiment.open_at
    if sort_by == "due_at":
        return Experiment.due_at
    if sort_by == "created_at":
        return Experiment.created_at
    return Experiment.updated_at


def list_admin_experiments(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 10,
    keyword: str = "",
    interaction_mode: str = "all",
    is_active: bool | None = None,
    is_published: bool | None = None,
    sort_by: str = "sort_order",
    sort_order: str = "asc",
) -> dict:
    statement = select(Experiment)
    cleaned_keyword = keyword.strip()
    if cleaned_keyword:
        statement = statement.where(
            or_(
                Experiment.title.ilike(f"%{cleaned_keyword}%"),
                Experiment.slug.ilike(f"%{cleaned_keyword}%"),
            )
        )
    if interaction_mode in {"native_editor", "guided_template"}:
        statement = statement.where(Experiment.interaction_mode == interaction_mode)
    if is_active is not None:
        statement = statement.where(Experiment.is_active == is_active)
    if is_published is not None:
        statement = statement.where(Experiment.is_published == is_published)

    sort_column = _sort_field(sort_by)
    if sort_order == "desc":
        statement = statement.order_by(sort_column.desc(), Experiment.id.desc())
    else:
        statement = statement.order_by(sort_column.asc(), Experiment.id.asc())

    total_statement = select(func.count()).select_from(statement.subquery())
    total = int(db.execute(total_statement).scalar_one() or 0)
    total_pages = ceil(total / page_size) if total > 0 else 0
    offset = (page - 1) * page_size
    rows = list(db.execute(statement.offset(offset).limit(page_size)).scalars().all())
    return {
        "items": rows,
        "total": total,
        "page": int(page),
        "page_size": int(page_size),
        "total_pages": int(total_pages),
    }


def create_admin_experiment(db: Session, payload: dict) -> Experiment:
    experiment = Experiment(**payload)
    db.add(experiment)
    db.commit()
    db.refresh(experiment)
    return experiment


def update_admin_experiment(db: Session, *, experiment: Experiment, payload: dict) -> Experiment:
    for key, value in payload.items():
        setattr(experiment, key, value)
    db.add(experiment)
    db.commit()
    db.refresh(experiment)
    return experiment


def delete_admin_experiment(db: Session, *, experiment: Experiment) -> None:
    db.delete(experiment)
    db.commit()


def update_settings(db: Session, experiment: Experiment, settings_in: ExperimentSettingsUpdate) -> Experiment:
    payload = settings_in.model_dump()
    for key, value in payload.items():
        setattr(experiment, key, value)
    db.add(experiment)
    db.commit()
    db.refresh(experiment)
    return experiment
