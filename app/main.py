from fastapi import FastAPI
from sqlalchemy import text
from app.api.auth import router as auth_router
from app.core.database import engine
from app.api import auth
from app.api.roles import router as roles_router
from app.api.users import router as users_router
from app.api import fui
from app.api.fui_analysis import router as fui_analysis_router
from app.api.fui_recommendation import router as fui_recommendation_router

app = FastAPI(
    title="FUI Management API",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(roles_router)
app.include_router(users_router)
app.include_router(
    fui.router,
    prefix="/api/fui",
    tags=["FUI"]
)
app.include_router(fui_analysis_router)
app.include_router(
    fui_recommendation_router
)

@app.get("/")
def root():
    return {
        "application": "FUI Management API",
        "status": "running"
    }


@app.get("/health/db")
def db_health():

    with engine.connect() as conn:

        result = conn.execute(
            text("SELECT NOW()")
        )

        current_time = result.scalar()

    return {
        "database": "connected",
        "server_time": str(current_time)
    }
