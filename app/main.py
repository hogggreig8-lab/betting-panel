from fastapi import FastAPI, Request
from telebot.types import Update
from app.core.join_requests_bot import bot
from app.core.visitor_tracking import BOT_TOKEN
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
import os
from fastapi.staticfiles import StaticFiles

Base.metadata.create_all(bind=engine)

app = FastAPI()
WEBHOOK_PATH = f"/telegram-webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"https://goldenfrog.top{WEBHOOK_PATH}"
@app.on_event("startup")
def startup_event():
    start_backup_worker()

    bot.remove_webhook()
    bot.set_webhook(
        url=WEBHOOK_URL,
        allowed_updates=["chat_join_request"]
    )
@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data)

    bot.process_new_updates([update])

    return {"ok": True}
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
os.makedirs(os.getenv("UPLOAD_DIR", "app/static/uploads"), exist_ok=True)

app.mount(
    "/uploads",
    StaticFiles(directory=os.getenv("UPLOAD_DIR", "app/static/uploads")),
    name="uploads"
)
app.include_router(public_router)
app.include_router(admin_router)