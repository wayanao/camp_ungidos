from fastapi import APIRouter

from controllers.auth_controller import login_controller
from schemas.user_schema import LoginRequest


router = APIRouter(prefix="/auth", tags=["auth"])
legacy_router = APIRouter(tags=["auth"])


@router.post("/login")
def login(data: LoginRequest):
    return login_controller(data)


@legacy_router.post("/login")
def legacy_login(data: LoginRequest):
    return login_controller(data)
