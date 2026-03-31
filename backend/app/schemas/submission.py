from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SubmissionStatus = Literal["draft", "submitted"]
ReviewStatus = Literal["pending", "passed", "failed"]


class CodeSubmissionCreate(BaseModel):
    experiment_id: int
    code: str = Field(min_length=1)
    run_output: str | None = None
    is_passed: bool | None = None


class CodeSubmissionUpdate(BaseModel):
    code: str | None = None
    run_output: str | None = None
    is_passed: bool | None = None


class CodeSubmissionRead(BaseModel):
    id: int
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


class CodeSubmissionListItem(BaseModel):
    id: int
    experiment_id: int
    status: SubmissionStatus
    review_status: ReviewStatus
    reviewed_at: datetime | None
    version: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class CodeSubmissionHistoryItem(CodeSubmissionListItem):
    pass


class WorkspaceStatusRead(BaseModel):
    experiment_id: int
    is_locked: bool
    latest_submission_id: int | None
    latest_version: int | None
    latest_status: SubmissionStatus | None
    is_published: bool
    is_open: bool
    is_overdue: bool
    can_edit: bool
    can_run: bool
    can_save_draft: bool
    can_submit: bool
    message: str
