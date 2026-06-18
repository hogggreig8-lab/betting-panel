import telebot
from datetime import datetime

from app.core.database import SessionLocal
from app.core.visitor_tracking import BOT_TOKEN, CHAT_ID
from app.models.join_request import JoinRequest


bot = telebot.TeleBot(BOT_TOKEN)


@bot.chat_join_request_handler()
def handle_join_request(join_request):
    user = join_request.from_user
    chat = join_request.chat

    db = SessionLocal()
    try:
        existing = (
            db.query(JoinRequest)
            .filter(JoinRequest.telegram_user_id == str(user.id))
            .first()
        )

        if existing:
            return

        username = user.username or ""
        first_name = user.first_name or ""
        last_name = user.last_name or ""

        request_row = JoinRequest(
            telegram_user_id=str(user.id),
            username=username,
            first_name=first_name,
            last_name=last_name,
            channel_title=chat.title or ""
        )

        db.add(request_row)
        db.commit()

        username_text = f"@{username}" if username else "нет username"
        full_name = f"{first_name} {last_name}".strip()

        text = (
            "✅📲 <b>Новая заявка</b>\n\n"
            f"👤 <b>Имя:</b> {full_name or 'не указано'}\n"
            f"🔗 <b>Username:</b> {username_text}"
        )

        bot.send_message(
            CHAT_ID,
            text,
            parse_mode="HTML"
        )

    finally:
        db.close()