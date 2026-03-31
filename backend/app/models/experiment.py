'''
Author: yumiazusa
Date: 2026-03-22 01:41:35
LastEditors: yumiazusa
LastEditTime: 2026-03-25 00:45:19
FilePath: /pythonclass/backend/app/models/experiment.py
Description: 
'''
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Integer, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    instruction_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    starter_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    interaction_mode: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="native_editor",
        server_default=text("'native_editor'"),
        index=True,
    )
    template_type: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    template_schema: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    code_template: Mapped[str | None] = mapped_column(Text, nullable=True)
    import_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    allow_edit_generated_code: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("1"),
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    open_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    submissions: Mapped[list["CodeSubmission"]] = relationship(
        back_populates="experiment",
        cascade="all, delete-orphan",
    )
