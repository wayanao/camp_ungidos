from fastapi import APIRouter

from controllers.person_controller import (
    add_charge_controller,
    add_payment_controller,
    all_payments_controller,
    create_person_controller,
    dashboard_controller,
    delete_person_controller,
    debtors_report_controller,
    list_people_controller,
    person_balance_controller,
    person_detail_controller,
    update_person_controller,
)
from schemas.person_schema import (
    ChargeCreate,
    ChargeResponse,
    DashboardResponse,
    PaymentCreate,
    PaymentResponse,
    PersonBalanceResponse,
    PersonCreate,
    PersonDetailResponse,
    PersonResponse,
    PersonUpdate,
)


router = APIRouter(prefix="/people", tags=["people"])
reports_router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", response_model=PersonResponse, status_code=201)
def create_person(data: PersonCreate):
    return create_person_controller(data)


@router.get("", response_model=list[PersonResponse])
def list_people():
    return list_people_controller()


@router.put("/{person_id}", response_model=PersonResponse)
def update_person(person_id: int, data: PersonUpdate):
    return update_person_controller(person_id, data)


@router.delete("/{person_id}", status_code=204)
def delete_person(person_id: int):
    delete_person_controller(person_id)


@router.get("/{person_id}", response_model=PersonDetailResponse)
def get_person_detail(person_id: int):
    return person_detail_controller(person_id)


@router.get("/{person_id}/balance", response_model=PersonBalanceResponse)
def get_person_balance(person_id: int):
    return person_balance_controller(person_id)


@router.post("/{person_id}/charges", response_model=ChargeResponse, status_code=201)
def create_charge(person_id: int, data: ChargeCreate):
    return add_charge_controller(person_id, data)


@router.post("/{person_id}/payments", response_model=PaymentResponse, status_code=201)
def create_payment(person_id: int, data: PaymentCreate):
    return add_payment_controller(person_id, data)


@reports_router.get("/debtors", response_model=list[PersonBalanceResponse])
def debtors_report():
    return debtors_report_controller()


@reports_router.get("/dashboard", response_model=DashboardResponse)
def dashboard():
    return dashboard_controller()


@reports_router.get("/all-payments")
def all_payments():
    return all_payments_controller()
