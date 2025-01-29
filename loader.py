from telethon import TelegramClient
from data.config import API_ID, API_HASH, BOT_TOKEN
from utils.db_api import postgres

db = postgres.Database()

class HTMLTelegramClient(TelegramClient):
    async def send_html_message(self, *args, **kwargs):
        kwargs['parse_mode'] = 'html'
        return await self.send_message(*args, **kwargs)
client = HTMLTelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
temp = { }
