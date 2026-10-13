from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.api.routes import (
    health,
    users,
    dashboard,
    sos,
    caregivers,
    activity,
    health_data,
    medications,
    appointments,
    notifications,
    chat,
    reports,
    auth,
)

configure_logging()
settings = get_settings()

app = FastAPI(title="Sahaara Intelligent ElderCare API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in [
    health.router,
    auth.router,
    users.router,
    dashboard.router,
    sos.router,
    caregivers.router,
    activity.router,
    health_data.router,
    medications.router,
    appointments.router,
    notifications.router,
    chat.router,
    reports.router,
]:
    app.include_router(router, prefix=settings.api_v1_prefix)

@app.get("/")
def root():
    return {"service": "Sahaara API", "status": "running"}