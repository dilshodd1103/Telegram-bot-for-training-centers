import asyncio
from telethon import events
from keyboards.default.admin_menu import admin
from keyboards.inline.confirm_buttons import confirm_delete_buttons
from keyboards.inline.kurslar import kurslar
from loader import client, db, temp


async def is_user_admin(user_id: int) -> bool:
    """Adminlikni tekshiruvchi yordamchi funksiya"""
    return await db.check_admin(selected_data=user_id)


@client.on(events.NewMessage(pattern="Kursni o'chirish"))
async def delete_kurs(event):
    user_id = event.sender_id
    if await is_user_admin(user_id):
        data = await db.select_all_kurs()
        if data:
            buttons = kurslar(data)
            await event.respond("<b>Barcha kurslarimiz</b>", parse_mode='html', buttons=None)
            await event.respond("<b>O'chirmoqchi bo'lgan kursni tanlang:</b>", buttons=buttons, parse_mode='html')
            temp[user_id] = {"state": "select_kurs"}
        else:
            await event.respond("<b>Kurslar mavjud emas</b>", parse_mode='html')


@client.on(events.CallbackQuery(pattern="^kurs_(\\d+)$"))
async def select_kurs(event):
    user_id = event.sender_id
    if temp.get(user_id, {}).get("state") == "select_kurs" and await is_user_admin(user_id):
        kurs_id = int(event.data_match.group(1))
        kurs = await db.select_kurs(kurs_id)
        if kurs:
            buttons = confirm_delete_buttons(kurs_id)
            await event.respond(f"<b>{kurs[1]} - kursini o'chirishni xohlaysizmi❗</b>", buttons=buttons, parse_mode='html')
            temp[user_id] = {"state": "confirm_delete", "kurs_id": kurs_id}
        else:
            await event.respond("<b>Kurs topilmadi!</b>", parse_mode='html')


@client.on(events.CallbackQuery(pattern="^confirm_yes_(\\d+)$"))
async def delete_confirmed(event):
    user_id = event.sender_id
    if temp.get(user_id, {}).get("state") == "confirm_delete" and await is_user_admin(user_id):
        kurs_id = int(event.data_match.group(1))
        kurs = await db.select_kurs(kurs_id)
        if kurs:
            await db.delete_kurs(kurs_id)
            await event.respond(f"<b>{kurs[1]} - kursi muvaffaqiyatli o'chirildi❗</b>", buttons=admin, parse_mode='html')
            temp.pop(user_id, None)


@client.on(events.CallbackQuery(pattern="^confirm_no_(\\d+)$"))
async def delete_canceled(event):
    user_id = event.sender_id
    if temp.get(user_id, {}).get("state") == "confirm_delete" and await is_user_admin(user_id):
        await event.respond("<b>Kursni o'chirish bekor qilindi.</b>", buttons=admin, parse_mode='html')
        temp.pop(user_id, None)


@client.on(events.CallbackQuery(pattern="back"))
async def back_to_menu(event):
    user_id = event.sender_id
    if temp.get(user_id, {}).get("state") == "select_kurs" and await is_user_admin(user_id):
        await event.respond("<i>Admin panel :</i>", buttons=admin, parse_mode='html')
        temp.pop(user_id, None)


@client.on(events.NewMessage())
async def handle_fallback(event):
    user_id = event.sender_id
    state = temp.get(user_id, {}).get("state")

    if state == "select_kurs" or state == "confirm_delete":
        warning_message = await event.respond("<b>Menuga qaytish uchun 'Ortga' tugmasini bosing.</b>", parse_mode='html')
        await asyncio.sleep(3)
        await client.delete_messages(user_id, [event.message.id, warning_message.id])
