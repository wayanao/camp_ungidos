from fastapi import HTTPException

from services.auth_service import authenticate_user


def login_controller(data):
    user = authenticate_user(data.email, data.password)

    if not user:
        raise HTTPException(status_code=401, detail="Credenciales invalidas")

    return {
        "message": "Login exitoso",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "rol": user["role"],
            "role": user["role"],
        },
    }


#holaaaaaaaaaaaa