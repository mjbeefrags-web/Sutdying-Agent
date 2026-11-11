from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentRead(BaseModel):
    id: UUID
    course_id: UUID
    title: str
    filename: str
    version: int
    status: str
    error_code: str | None
    size_bytes: int
    page_count: int | None
    created_at: datetime
    updated_at: datetime
