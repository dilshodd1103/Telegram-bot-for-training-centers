import asyncio
from datetime import datetime
from telethon import events, Button

from keyboards.default.admin_menu import admin
from keyboards.default.bekor_qilish import bekor, bekor1
from loader import client, db

# Lug‘at: foydalanuvchi holatini saqlash
user_states = {}

# Holatlarni aniqlash
STATE_NONE = "NONE"
STATE_REKLAMA = "REKLAMA"

async def is_user_admin(user_id: int) -> bool:
    """Adminlikni tekshiruvchi yordamchi funksiya"""
    return await db.check_admin(selected_data=user_id)


@client.on(events.NewMessage(pattern="Reklama"))
async def reklama(event):
    if await is_user_admin(event.sender_id):
        await event.respond(
            "<b>Yaxshi, reklama postini yuboring : </b>\n<i>(Text, Rasm, Video, Dokument)</i>\n"
            "<i>❗️Yuborgan postingiz shu holicha barcha foydalanuvchilarga yuboriladi\nOrtga qaytishingiz ham mumkin</i>",
            buttons=bekor1,
            parse_mode="html",
        )
        user_states[event.sender_id] = STATE_REKLAMA


@client.on(events.NewMessage(pattern='Bekor qilish'))
async def ortga(event):
    if user_states.get(event.sender_id) == STATE_REKLAMA and await is_user_admin(event.sender_id):
        await event.respond(
            "<b><i>Menu : </i></b>",
            buttons=admin,
            parse_mode="html",
        )
        user_states[event.sender_id] = STATE_NONE  # Holatni reset qilish


@client.on(events.NewMessage(func=lambda e: user_states.get(e.sender_id) == STATE_REKLAMA))
async def reklama2(event):
    if await is_user_admin(event.sender_id):
        if event.text == "Reklama":
            return
        content_type = None
        content = None

        # Kontentni aniqlash
        if not event.media:  # Faqat matn
            content_type = "text"
            content = event.raw_text
        elif event.photo:  # Rasm
            content_type = "photo"
            content = event.photo
        elif event.video:  # Video
            content_type = "video"
            content = event.video
        elif event.document:  # Dokument
            content_type = "document"
            content = event.document

        data_users = await db.select_all_users()
        n = 0
        successful = 0

        # Foydalanuvchilarga xabar yuborish
        for user in data_users:
            try:
                user_id = user[6]
                await client.send_message(user_id, event.message)
                successful += 1
            except Exception:
                n += 1
            finally:
                await asyncio.sleep(0.1)

        await event.respond(
            f"<b>✅Yuborildi : <i>{successful}</i>\n❌Yuborilmadi : <i>{n}</i></b>",
            buttons=admin, parse_mode="html",
        )
        await db.add_admin_reklama(
            content_type=content_type,
            content=str(content),
            sent_date=datetime.now(),
        )
        user_states[event.sender_id] = STATE_NONE  # Holatni reset qilish
