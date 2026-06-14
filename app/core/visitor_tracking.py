from datetime import datetime

import requests
import re
from app.core.database import SessionLocal
from app.models.visit import Visit
from sqlalchemy.exc import IntegrityError

BOT_TOKEN = "8325927637:AAFc6Az-tIce3gXSGy45EIcsK3wrkk5YafY"
CHAT_ID = "1659935851"


BOT_KEYWORDS = [
    "bot",
    "crawler",
    "spider",
    "preview",
    "facebookexternalhit",
    "telegrambot",
    "whatsapp",
    "slurp",
    "bing",
    "yandex",
    "google",
    "ahrefs",
    "semrush",
    "curl",
    "wget",
    "python-requests",
]


def is_bot(user_agent: str):
    if not user_agent:
        return True

    ua = user_agent.lower()

    for keyword in BOT_KEYWORDS:
        if keyword in ua:
            return True

    return False


def get_client_ip(request):
    forwarded = request.headers.get("x-forwarded-for")

    if forwarded:
        return forwarded.split(",")[0].strip()

    real_ip = request.headers.get("x-real-ip")

    if real_ip:
        return real_ip.strip()

    return request.client.host


def detect_device(user_agent: str):
    ua = user_agent

    if not ua:
        return "Unknown"

    ua_lower = ua.lower()

    if "iphone" in ua_lower:
        return "iPhone / iOS"

    if "ipad" in ua_lower:
        return "iPad / iOS"

    if "android" in ua_lower:
        match = re.search(r"Android [^;]+;\s?([^;)]+)", ua)

        if match:
            model = match.group(1).strip()

            model = model.replace("Build", "").strip()

            return f"Android — {model}"

        return "Android"

    if "windows" in ua_lower:
        return "Desktop — Windows"

    if "macintosh" in ua_lower or "mac os" in ua_lower:
        return "Desktop — macOS"

    if "linux" in ua_lower:
        return "Desktop — Linux"

    return "Desktop"


def get_geo(ip: str):
    try:
        response = requests.get(
            f"https://ipwho.is/{ip}",
            timeout=2
        )

        data = response.json()

        if not data.get("success"):
            return "Unknown", ""

        country = data.get("country", "Unknown")
        country_code = data.get("country_code", "")

        return country, country_code

    except Exception:
        return "Unknown", ""


def country_flag(country_code: str):
    if not country_code or len(country_code) != 2:
        return ""

    return chr(ord(country_code[0].upper()) + 127397) + chr(ord(country_code[1].upper()) + 127397)


def send_telegram(text: str):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            },
            timeout=3
        )
    except Exception:
        pass


def track_unique_visit(request):
    path = request.url.path

    if path.startswith("/static"):
        return

    if path.startswith("/admin"):
        return

    if path in ["/favicon.ico", "/robots.txt"]:
        return

    user_agent = request.headers.get("user-agent", "")

    if is_bot(user_agent):
        return

    ip = get_client_ip(request)
    domain = request.headers.get("host", "Unknown")
    device = detect_device(user_agent)

    db = SessionLocal()

    try:
        existing = (
            db.query(Visit)
            .filter(Visit.ip == ip)
            .filter(Visit.user_agent == user_agent)
            .first()
        )

        if existing:
            return

        country, country_code = get_geo(ip)
        flag = country_flag(country_code)

        visit = Visit(
            ip=ip,
            user_agent=user_agent[:500],
            device=device,
            country=country,
            country_code=country_code,
            domain=domain,
        )

        try:
            db.add(visit)
            db.commit()
        except IntegrityError:
            db.rollback()
            return

        text = (
            "👁 <b>Новое посещение</b>\n\n"
            f"🌎 <b>ГЕО:</b> {flag} {country}\n"
            f"📱 <b>Устройство:</b> {device}\n"
        )

        send_telegram(text)

    finally:
        db.close()