import os
import time
import shutil
import threading
from datetime import datetime

import requests

from app.core.visitor_tracking import BOT_TOKEN, CHAT_ID


DB_PATH = "sports.db"
BACKUP_DIR = "app/static/backups"


def send_backup_to_telegram(file_path: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"

    with open(file_path, "rb") as file:
        requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "caption": f"💾 Backup DB\n🕒 {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
            },
            files={
                "document": file
            },
            timeout=20
        )


def create_backup():
    if not os.path.exists(DB_PATH):
        return

    os.makedirs(BACKUP_DIR, exist_ok=True)

    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    backup_path = os.path.join(
        BACKUP_DIR,
        f"sports_backup_{now}.db"
    )

    shutil.copy2(DB_PATH, backup_path)

    send_backup_to_telegram(backup_path)


def backup_loop():
    last_backup_date = None

    while True:
        now = datetime.now()

        if now.hour == 3 and last_backup_date != now.date():
            try:
                create_backup()
                last_backup_date = now.date()
            except Exception:
                pass

        time.sleep(60 * 10)


def start_backup_worker():
    thread = threading.Thread(
        target=backup_loop,
        daemon=True
    )

    thread.start()