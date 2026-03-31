from datetime import datetime

from pydantic import BaseModel

from app.schemas.experiment import InteractionModeType
from app.schemas.submission import ReviewStatus, SubmissionStatus
from app.schemas.user import RoleType


class StudentDashboardProfile(BaseModel):
    id: int
    username: str
    full_name: str | None
    student_no: str | None
    class_name: str | None
    role: RoleType


class StudentDashboardSummary(BaseModel):
    total_experiments: int
    submitted_count: int
    passed_count: int
    failed_count: int
    pending_count: int
    not_started_count: int


class StudentDashboardRecentItem(BaseModel):
    experiment_id: int
    title: str
    interaction_mode: InteractionModeType
    latest_status: SubmissionStatus
    review_status: ReviewStatus
    latest_updated_at: datetime


class StudentDashboardRead(BaseModel):
    profile: StudentDashboardProfile
    summary: StudentDashboardSummary
    recent_items: list[StudentDashboardRecentItem]
