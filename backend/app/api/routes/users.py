from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.deps import DBSession

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/test")
def users_db_test(db: DBSession) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
        return {"database": "ok"}
    except SQLAlchemyError:
        return {"database": "error"}
