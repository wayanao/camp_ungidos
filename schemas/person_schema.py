from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class PersonCreate(BaseModel):
    first_name: str = Field(min_length=2, max_length=100)
    last_name: str = Field(min_length=2, max_length=100)
    document: str = Field(min_length=4, max_length=30)
    phone: str | None = Field(default=None, max_length=30)
    age: int | None = Field(default=None, ge=0, le=120)
    church: str | None = Field(default=None, max_length=120)
    guardian_name: str | None = Field(default=None, max_length=120)
    guardian_phone: str | None = Field(default=None, max_length=30)
    eps: str | None = Field(default=None, max_length=120)
    blood_type: str | None = Field(default=None, max_length=5)
    allergies: str | None = Field(default=None, max_length=500)
    medications: str | None = Field(default=None, max_length=500)
    medical_conditions: str | None = Field(default=None, max_length=500)
    dietary_restrictions: str | None = Field(default=None, max_length=500)
    emergency_contact_name: str | None = Field(default=None, max_length=120)
    emergency_contact_phone: str | None = Field(default=None, max_length=30)
    insurance_provider: str | None = Field(default=None, max_length=120)
    base_fee: float = Field(default=0, ge=0)
    status: str = Field(default="registrado", max_length=40)
    notes: str | None = Field(default=None, max_length=500)


class PersonResponse(PersonCreate):
    id: int
    created_at: datetime


class PersonUpdate(PersonCreate):
    pass


class ChargeCreate(BaseModel):
    concept: str = Field(min_length=2, max_length=120)
    amount: float = Field(gt=0)
    due_date: date | None = None
    notes: str | None = Field(default=None, max_length=300)


class ChargeResponse(ChargeCreate):
    id: int
    person_id: int
    created_at: datetime


class PaymentCreate(BaseModel):
    amount: float = Field(gt=0)
    payment_date: date
    payment_method: str = Field(min_length=2, max_length=50)
    reference: str | None = Field(default=None, max_length=80)
    notes: str | None = Field(default=None, max_length=300)


class PaymentResponse(PaymentCreate):
    id: int
    person_id: int
    created_at: datetime


class PersonBalanceResponse(BaseModel):
    person_id: int
    full_name: str
    total_charged: float
    total_paid: float
    balance: float
    status: str


class PersonDetailResponse(BaseModel):
    person: PersonResponse
    charges: list[ChargeResponse]
    payments: list[PaymentResponse]
    balance: PersonBalanceResponse


class DashboardResponse(BaseModel):
    total_people: int
    total_charged: float
    total_paid: float
    total_pending: float
    debtors: int
