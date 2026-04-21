from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.database import init_db
from routes.auth_routes import legacy_router
from routes.auth_routes import router as auth_router
from routes.person_routes import reports_router
from routes.person_routes import router as people_router


app = FastAPI(
    title="Campamento Cristiano API",
    description="API para registro de personas, pagos y reportes de deuda.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


#@app.on_event("startup")
#def startup_event():
    #init_db()


@app.get("/")
def healthcheck():
    return {"message": "Campamento Cristiano API activa"}


app.include_router(auth_router)
app.include_router(legacy_router)
app.include_router(people_router)
app.include_router(reports_router)
