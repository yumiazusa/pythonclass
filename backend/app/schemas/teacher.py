from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.submission import ReviewStatus, SubmissionStatus


class TeacherExperimentOverviewItem(BaseModel):
    experiment_id: int
    title: str
    is_published: bool
    open_at: datetime | None
    due_at: datetime | None
    total_students_with_records: int
    submitted_count: int
    draft_count: int
    locked_count: int
    reviewed_count: int
    passed_count: int
    failed_count: int
    pending_review_count: int
    updated_at: datetime | None


class TeacherExperimentStudentStatusItem(BaseModel):
    user_id: int
    username: str
    full_name: str | None
    student_no: str | None
    class_name: str | None
    latest_submission_id: int
    latest_version: int
    latest_status: SubmissionStatus
    is_locked: bool
    review_status: ReviewStatus
    reviewed_at: datetime | None
    needs_review: bool
    latest_updated_at: datetime
    can_reopen: bool
    has_final_submission: bool


class TeacherExperimentStudentStatusPage(BaseModel):
    items: list[TeacherExperimentStudentStatusItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class TeacherSubmissionDetailRead(BaseModel):
    id: int
    user_id: int
    experiment_id: int
    code: str
    status: SubmissionStatus
    run_output: str | None
    is_passed: bool | None
    review_status: ReviewStatus
    review_comment: str | None
    reviewed_by: int | None
    reviewed_at: datetime | None
    version: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TeacherReturnResponse(BaseModel):
    experiment_id: int
    user_id: int
    reopened_submission_id: int
    reopened_version: int
    latest_status: SubmissionStatus
    message: str


class TeacherSubmissionReviewUpdate(BaseModel):
    review_status: ReviewStatus
    review_comment: str | None = None


class TeacherBatchReviewRequest(BaseModel):
    submission_ids: list[int] = Field(min_length=1)
    review_status: ReviewStatus
    review_comment: str | None = None


class TeacherBatchReviewFailedItem(BaseModel):
    submission_id: int
    reason: str


class TeacherBatchReviewResponse(BaseModel):
    success_count: int
    failed_count: int
    success_submission_ids: list[int]
    failed_items: list[TeacherBatchReviewFailedItem]
    message: str


class TeacherBatchReturnRequest(BaseModel):
    user_ids: list[int] = Field(min_length=1)


class TeacherBatchReturnFailedItem(BaseModel):
    user_id: int
    reason: str


class TeacherBatchReturnResponse(BaseModel):
    success_count: int
    failed_count: int
    success_user_ids: list[int]
    failed_items: list[TeacherBatchReturnFailedItem]
    message: str


class TeacherStudentImportFailedItem(BaseModel):
    row: int
    student_no: str
    reason: str


class TeacherStudentImportResponse(BaseModel):
    total_rows: int
    created_count: int
    updated_count: int
    skipped_count: int
    failed_items: list[TeacherStudentImportFailedItem]
    message: str


class TeacherStudentAccountItem(BaseModel):
    user_id: int
    username: str
    full_name: str | None
    student_no: str | None
    class_name: str | None
    role: str
    is_enabled: bool
    created_at: datetime


class TeacherStudentAccountPage(BaseModel):
    items: list[TeacherStudentAccountItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class TeacherStudentBatchActionFailedItem(BaseModel):
    user_id: int
    reason: str


class TeacherStudentBatchStatusRequest(BaseModel):
    user_ids: list[int] = Field(min_length=1)


class TeacherStudentStatusUpdateResponse(BaseModel):
    user_id: int
    is_enabled: bool
    message: str


class TeacherStudentBatchStatusUpdateResponse(BaseModel):
    success_count: int
    failed_count: int
    success_user_ids: list[int]
    failed_items: list[TeacherStudentBatchActionFailedItem]
    message: str


class TeacherStudentBatchPasswordResetRequest(BaseModel):
    user_ids: list[int] = Field(min_length=1)
    new_password: str = Field(min_length=6, max_length=128)


class TeacherStudentBatchPasswordResetResponse(BaseModel):
    success_count: int
    failed_count: int
    success_user_ids: list[int]
    failed_items: list[TeacherStudentBatchActionFailedItem]
    message: str


class TeacherExperimentClassSummaryItem(BaseModel):
    class_name: str
    total_students: int
    submitted_count: int
    passed_count: int
    failed_count: int
    pending_review_count: int
    not_submitted_count: int
