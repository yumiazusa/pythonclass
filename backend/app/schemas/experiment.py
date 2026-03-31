from datetime import datetime
from typing import Any
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

InteractionModeType = Literal["native_editor", "guided_template"]


class ExperimentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    slug: str = Field(min_length=1, max_length=120)
    description: str | None = None
    instruction_content: str | None = None
    starter_code: str | None = None
    interaction_mode: InteractionModeType = "native_editor"
    template_type: str | None = None
    template_schema: dict[str, Any] | None = None
    code_template: str | None = None
    import_config: dict[str, Any] | None = None
    allow_edit_generated_code: bool = True
    sort_order: int = 0
    is_active: bool = True
    is_published: bool = False
    open_at: datetime | None = None
    due_at: datetime | None = None


class ExperimentSettingsUpdate(BaseModel):
    is_published: bool
    open_at: datetime | None = None
    due_at: datetime | None = None


class ExperimentRead(BaseModel):
    id: int
    title: str
    slug: str
    description: str | None
    instruction_content: str | None
    starter_code: str | None
    interaction_mode: InteractionModeType
    template_type: str | None
    template_schema: dict[str, Any] | None
    code_template: str | None
    import_config: dict[str, Any] | None
    allow_edit_generated_code: bool
    sort_order: int
    is_active: bool
    is_published: bool
    open_at: datetime | None
    due_at: datetime | None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class GuidedImportValidateRequest(BaseModel):
    custom_import_text: str = ""


class GuidedImportValidateResponse(BaseModel):
    valid: bool
    normalized_imports: list[str]
    errors: list[str]
