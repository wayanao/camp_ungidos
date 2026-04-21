from fastapi import APIRouter

from controllers.expense_controller import (
    create_expense_controller,
    delete_expense_controller,
    list_expenses_controller,
)
from schemas.expense_schema import ExpenseCreate, ExpenseResponse

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.get("", response_model=list[ExpenseResponse])
def list_expenses():
    return list_expenses_controller()


@router.post("", response_model=ExpenseResponse, status_code=201)
def create_expense(data: ExpenseCreate):
    return create_expense_controller(data)


@router.delete("/{expense_id}", status_code=204)
def delete_expense(expense_id: int):
    delete_expense_controller(expense_id)
