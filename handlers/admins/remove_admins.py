from telethon import events

from data.config import ADMINS
from keyboards.default.admin_menu import admin
from keyboards.default.get_admin import get_admin
from keyboards.inline.admin import admin_list_keyboard, adminlar
from loader import db, client, temp


async def is_user_admin(user_id: int) -> bool:
    """Adminlikni tekshiruvchi yordamchi funksiya."""
    return await db.check_admin(selected_data=user_id)


@client.on(events.NewMessage(pattern="_Adminlar"))
async def admins(event):
    user_id = event.sender_id
    if await is_user_admin(user_id):
        await event.respond("<b>Adminlar bilan ishlash:</b>", buttons=get_admin, parse_mode='html')
        temp[user_id] = {"state": "admins_see"}


@client.on(events.NewMessage(pattern="↩️Ortga"))
async def back_admin(event):
    user_id = event.sender_id
    if temp.get(user_id, {}).get("state") == "admins_see":
        await event.respond("<b>Admin menu:</b>", buttons=admin, parse_mode='html')
        temp.pop(user_id, None)


@client.on(events.NewMessage(pattern="➕Admin tayinlash", func=lambda e: e.chat_id in ADMINS))
async def assign_admin(event):
    user_id = event.sender_id
    if temp.get(user_id, {}).get("state") == "admins_see":
        data = await db.select_all_users()
        if data:
            await event.respond(f"<b>Obunachilar soni:</b> <i>{len(data)} ta</i>", parse_mode='html')
            buttons = adminlar(data)
            await event.respond("<b>Admin tayinlang:</b>", buttons=buttons, parse_mode='html')
        else:
            await event.respond("<b>Obunachilar mavjud emas</b>", parse_mode='html')
        temp[user_id] = {"state": "add_admin"}


@client.on(events.CallbackQuery(pattern="set_"))
async def assign_admin_handler(event):
    user_id = event.sender_id
    selected_user_id = int(event.data.decode("utf-8").split("_")[1])

    if temp.get(user_id, {}).get("state") == "add_admin":
        is_admin = await db.check_admin(selected_user_id)
        if is_admin:
            await event.respond(f"<b>⚠️ Foydalanuvchi allaqachon admin!</b>", parse_mode='html', buttons=get_admin)
        else:
            await db.set_admin(selected_user_id)
            await event.respond(f"<b>✅ Foydalanuvchi admin sifatida belgilandi.</b>", parse_mode='html')
        temp[user_id] = {"state": "admins_see"}
    else:
        await event.respond("Holat noto‘g‘ri! Iltimos, menyudan boshlang.", parse_mode='html')


@client.on(events.NewMessage(pattern="👀Adminlarni ko'rish", func=lambda e: e.chat_id in ADMINS))
async def view_admins(event):
    user_id = event.sender_id
    if temp.get(user_id, {}).get("state") == "admins_see":
        data = await db.get_admin()
        admins = [user for user in data if user['admin']]
        if not admins:
            await event.respond("Hozirda hech qanday admin topilmadi.", parse_mode='html')
            return
        keyboard = admin_list_keyboard(admins)
        await event.respond(f"<b>Adminlar soni:</b> <i>{len(admins)} ta</i>", parse_mode='html')
        await event.respond(f"<b>Adminlikdan olib tashlash uchun tanlang:</b> ", buttons=keyboard, parse_mode='html')
        temp[user_id] = {'state': 'remove_admin'}


@client.on(events.CallbackQuery(pattern="remove_admin_"))
async def remove_admin_handler(event):
    user_id = event.sender_id
    if temp.get(user_id, {}).get("state") == "remove_admin":
        callback_data = event.data.decode("utf-8")
        admin_id = int(callback_data.split("_")[-1])
        success = await db.remove_admin(admin_id)
        if success:
            await event.respond(f"<b>Admin <i>{admin_id}</i> adminlikdan olib tashlandi.</b>", parse_mode='html')
        else:
            await event.respond("Xatolik yuz berdi, iltimos keyinroq urinib ko'ring.", parse_mode='html')
        temp[user_id] = {'state': 'admin_see'}

@client.on(events.CallbackQuery(pattern="qaytish"))
async def admin_menu_back(event):
    user_id = event.sender_id
    if temp.get(user_id, {}).get("state") == "remove_admin":
        await event.respond("Adminlar bilan ishlash", buttons=get_admin)
        temp[user_id] = {'state': 'admins_see'}

@client.on(events.CallbackQuery(pattern="back1"))
async def admin_menu_back_set_admin(event):
    user_id = event.sender_id
    if temp.get(user_id, {}).get("state") == "add_admin":
        await event.respond("Adminlar bilan ishlash", buttons=get_admin)
        temp[user_id] = {'state': 'admins_see'}
