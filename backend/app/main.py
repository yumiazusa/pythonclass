from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.db.base_class import Base
from app.db.init_db import (
    ensure_database_exists,
    ensure_default_docs,
    ensure_experiment_schedule_columns,
    ensure_submission_review_columns,
    ensure_user_enabled_column,
    ensure_user_must_change_password_column,
    ensure_user_profile_columns,
)
from app.db.session import engine

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
)


@app.on_event("startup")
def startup_db_sync() -> None:
    ensure_database_exists()
    Base.metadata.create_all(bind=engine)
    ensure_experiment_schedule_columns()
    ensure_user_profile_columns()
    ensure_user_enabled_column()
    ensure_user_must_change_password_column()
    ensure_submission_review_columns()
    ensure_default_docs()


app.include_router(api_router)
