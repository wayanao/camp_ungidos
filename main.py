from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from config.database import init_db
from routes.auth_routes import legacy_router
from routes.auth_routes import router as auth_router
from routes.expense_routes import router as expense_router
from routes.person_routes import reports_router
from routes.person_routes import router as people_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Campamento Cristiano API",
    description="API para registro de personas, pagos y reportes de deuda.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    if request.method == "OPTIONS":
        response = JSONResponse(content={}, status_code=200)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept"
        return response
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


@app.get("/")
def healthcheck():
    return {"message": "Campamento Cristiano API activa", "version": "2.0"}


app.include_router(auth_router)
app.include_router(legacy_router)
app.include_router(people_router)
app.include_router(reports_router)
app.include_router(expense_router)
