from schemas.person_schema import ChargeCreate, PaymentCreate, PersonCreate, PersonUpdate
from services.person_service import (
    add_charge,
    add_payment,
    create_person,
    delete_person,
    get_dashboard,
    get_person_balance,
    get_person_detail,
    list_all_payments,
    list_debtors,
    list_people,
    update_person,
)


def create_person_controller(data: PersonCreate):
    return create_person(data)


def update_person_controller(person_id: int, data: PersonUpdate):
    return update_person(person_id, data)


def delete_person_controller(person_id: int):
    return delete_person(person_id)


def list_people_controller():
    return list_people()


def person_detail_controller(person_id: int):
    return get_person_detail(person_id)


def add_charge_controller(person_id: int, data: ChargeCreate):
    return add_charge(person_id, data)


def add_payment_controller(person_id: int, data: PaymentCreate):
    return add_payment(person_id, data)


def person_balance_controller(person_id: int):
    return get_person_balance(person_id)


def debtors_report_controller():
    return list_debtors()


def dashboard_controller():
    return get_dashboard()


def all_payments_controller():
    return list_all_payments()
