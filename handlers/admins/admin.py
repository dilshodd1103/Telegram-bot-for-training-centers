from telethon import events

from keyboards.default.admin_menu import admin
from loader import client, db


async def is_user_admin(user_id: int) -> bool:
    """Adminlikni tekshiruvchi yordamchi funksiya"""
    return await db.check_admin(user_id)


@client.on(events.NewMessage(pattern="Admin"))
async def admin_func(event: events.NewMessage.Event):
    if await is_user_admin(event.sender_id):
        await event.respond("Admin panel", buttons=admin)
