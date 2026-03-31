from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DBSession
from app.crud import crud_student
from app.schemas.student import StudentDashboardRead

router = APIRouter(prefix="/student", tags=["student"])


@router.get("/dashboard", response_model=StudentDashboardRead)
def get_student_dashboard(db: DBSession, current_user: CurrentUser) -> StudentDashboardRead:
    payload = crud_student.get_dashboard_payload(db, user_id=current_user.id)
    if not payload:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return StudentDashboardRead.model_validate(payload)
