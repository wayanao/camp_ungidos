from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from config.database import init_db
from routes.auth_routes import legacy_router
from routes.auth_routes import router as auth_router
from routes.expense_routes import router as expense_router
from routes.person_routes import reports_router
from routes.person_routes import router as people_router
from fastapi.middleware.cors import CORSMiddleware



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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://camp-ungidos.netlify.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
def healthcheck():
    return {"message": "Campamento Cristiano API activa", "version": "2.0"}


app.include_router(auth_router)
app.include_router(legacy_router)
app.include_router(people_router)
app.include_router(reports_router)
app.include_router(expense_router)
