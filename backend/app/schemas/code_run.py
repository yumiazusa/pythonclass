from typing import Literal

from pydantic import BaseModel, Field

CodeRunStatus = Literal["completed", "runtime_error", "timed_out", "blocked", "internal_error"]


class CodeRunRequest(BaseModel):
    code: str = Field(min_length=1)
    experiment_id: int = Field(gt=0)


class CodeRunResponse(BaseModel):
    success: bool
    status: CodeRunStatus
    stdout: str
    stderr: str
    returncode: int | None
    timed_out: bool
    execution_time_ms: int
    blocked: bool
    block_reason: str | None
