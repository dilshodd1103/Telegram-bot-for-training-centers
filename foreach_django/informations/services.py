import asyncio

from django.conf import settings
from telethon import TelegramClient


def get_bot_client():
    api_id = settings.TELEGRAM_API_ID
    api_hash = settings.TELEGRAM_API_HASH
    bot_token = settings.TELEGRAM_BOT_TOKEN
    return TelegramClient("bot", api_id, api_hash).start(bot_token=bot_token)


async def send_message_async(chat_id, message, img_path=None, video_path=None):
    client = TelegramClient("bot", settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH)
    await client.start(bot_token=settings.TELEGRAM_BOT_TOKEN)
    try:
        try:
            await client.get_input_entity(chat_id)
        except ValueError:
            return False

        if img_path:
            await client.send_file(chat_id, img_path, caption=message, parse_mode="html")
        elif video_path:
            await client.send_file(chat_id, video_path, caption=message, parse_mode="html")
        else:
            await client.send_message(chat_id, message, parse_mode="html")
        return True
    finally:
        await client.disconnect()


def send_message_to_subscriber_sync(chat_id, message, img_path=None, video_path=None):
    return asyncio.run(send_message_async(chat_id, message, img_path, video_path))
