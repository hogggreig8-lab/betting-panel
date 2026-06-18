from app.core.join_requests_bot import bot


if __name__ == "__main__":
    bot.remove_webhook()
    bot.infinity_polling(
        skip_pending=True,
        timeout=20,
        long_polling_timeout=20
    )