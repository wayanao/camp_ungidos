from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class ExpenseCreate(BaseModel):
    concept: str = Field(min_length=2, max_length=120)
    amount: float = Field(gt=0)
    date: date
    category: str = Field(default="general", max_length=60)
    notes: str | None = Field(default=None, max_length=300)


class ExpenseResponse(ExpenseCreate):
    id: int
    created_at: datetime
