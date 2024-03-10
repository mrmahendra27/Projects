from typing import Optional

from sqlmodel import SQLModel, Field


class Note(SQLModel, table=True):
    __tablename__ = "note"

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    name: str = Field(default=None, min_length=6, max_length=50, nullable=False)
    description: str = Field(
        default=None, min_length=10, max_length=500, nullable=False
    )
