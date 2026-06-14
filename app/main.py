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
Base.metadata.create_all(bind=engine)

app = FastAPI()
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