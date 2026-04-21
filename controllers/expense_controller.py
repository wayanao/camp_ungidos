from schemas.expense_schema import ExpenseCreate
from services.expense_service import create_expense, delete_expense, list_expenses


def list_expenses_controller():
    return list_expenses()


def create_expense_controller(data: ExpenseCreate):
    return create_expense(data)


def delete_expense_controller(expense_id: int):
    return delete_expense(expense_id)
