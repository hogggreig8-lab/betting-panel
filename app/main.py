from fastapi import FastAPI
import app.models.vip_prediction
from app.core.database import Base
from app.core.database import engine
import app.models.site_content
from app.routers.public import router as public_router
from app.routers.admin import router as admin_router
from fastapi.staticfiles import StaticFiles
import app.models.stat
import app.models.setting
import app.models.review
import app.models.visit
from app.core.visitor_tracking import track_unique_visit
from app.core.db_backup import start_backup_worker
import app.models.join_request
from app.core.join_requests_bot import start_join_requests_worker
Base.metadata.create_all(bind=engine)

app = FastAPI()
@app.on_event("startup")
def startup_event():
    start_backup_worker()
    start_join_requests_worker()
@app.middleware("http")
async def visitor_tracking_middleware(request, call_next):
    track_unique_visit(request)
    response = await call_next(request)
    return response
app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)
app.include_router(public_router)
app.include_router(admin_router)