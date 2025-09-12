#!/usr/bin/env python3
"""
Models for the standalone To-Do / Capture receipt flow.
This is intentionally separate from the daily brief models.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
try:
    # pydantic v2
    from pydantic import field_validator
except ImportError:  # pragma: no cover
    field_validator = None  # type: ignore


class ToDoAttachment(BaseModel):
    """Represents an attachment that was captured (e.g., image, file)."""

    type: str = Field(description="Attachment type, e.g., 'image', 'file', 'url'")
    url: Optional[str] = Field(default=None, description="Public or local URL to attachment")
    caption: Optional[str] = Field(default=None, description="Optional human-readable caption")


class ToDoItem(BaseModel):
    """A single actionable to-do item extracted from input."""

    title: str = Field(description="Concise action title")
    notes: Optional[str] = Field(default=None, description="Optional details or sub-steps")
    priority: Optional[str] = Field(default=None, description="low | medium | high")


class ToDoReceiptHeader(BaseModel):
    """Header metadata for the receipt."""

    title: str = Field(default="Capture Summary", description="Top title for the receipt")
    date_formatted: str = Field(description="Formatted date string for display")
    source_label: Optional[str] = Field(default=None, description="e.g., 'From Image Upload' or 'From Text Paste'")

    # Enforce a sane maximum for title to avoid visual overflow on narrow receipts
    if field_validator:
        @field_validator("title")
        def _cap_title(cls, v: str) -> str:  # type: ignore
            max_chars = 48
            return v if len(v) <= max_chars else (v[: max_chars - 1] + "…")


class ToDoReceiptSummary(BaseModel):
    """High-level AI summary of the uploaded content."""

    overview: str = Field(description="1-3 sentence summary of the content")
    key_points: Optional[List[str]] = Field(default=None, description="Bullet points of key insights")


class ToDoReceiptContent(BaseModel):
    """Complete content for rendering the To-Do capture receipt."""

    header: ToDoReceiptHeader
    summary: ToDoReceiptSummary
    todos: List[ToDoItem]
    attachments: Optional[List[ToDoAttachment]] = None
    tables: Optional[List["TableSection"]] = None


class TableSection(BaseModel):
    """A tabular section that can be rendered on the receipt."""

    title: Optional[str] = Field(default=None, description="Optional table title")
    columns: List[str] = Field(description="Column headers")
    rows: List[List[str]] = Field(description="Row values matching number of columns")


