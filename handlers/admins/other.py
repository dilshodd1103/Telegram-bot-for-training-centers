import datetime

import pytz
from telethon import events

from data.config import ADMINS
from keyboards.default.admin_menu import admin
from keyboards.default.all_user import all_user
from keyboards.default.menu import menu
from keyboards.inline.kurs_tahrirlash import user_ALL
from loader import db, client


async def is_user_admin(user_id: int) -> bool:
    """Adminlikni tekshiruvchi yordamchi funksiya"""
    return await db.check_admin(selected_data=user_id)


@client.on(events.NewMessage(pattern="Menu"))
async def menu1(event):
    if await is_user_admin(event.sender_id):
        await event.respond("<b>Foydalanuvchilar menusi : </b>", buttons=menu, parse_mode = 'html')


@client.on(events.NewMessage(pattern='Foydalanuvchilar soni'))
async def all_users(event):
    if await is_user_admin(event.sender_id):
        data = await db.count_users()
        await event.respond(f"<b>Foydalanuvchilar soni: </b>    <i>{data} ta </i>" , buttons=all_user, parse_mode = 'html')


@client.on(events.NewMessage(pattern='⚙️Admin menu'))
async def user_back(event):
    if await is_user_admin(event.sender_id):
        await event.respond("Admin menu", buttons=admin)


@client.on(events.NewMessage(pattern="Foydalanuvchilarni ko'rish"))
async def all_user_id(event):
    if await is_user_admin(event.sender_id):
        data = await db.select_all_users()
        buttons = user_ALL(data)
        await event.respond("<b>Barcha foydalanuvchilar</b>", buttons=buttons, parse_mode='html')


@client.on(events.CallbackQuery(pattern="wrong_number+"))
async def xato_raqam(event):
    id = int(event.data.decode('utf-8').split(':')[1])
    answer = (
        "<b>Botga kiritgan raqamingiz orqali sizga bog'lana olmadik\n\n"
        "Iltimos, sizga bog'lana olishimiz mumkin bo'lgan raqamingizni botga kiriting❗️</b>"
    )
    await client.send_message(id, answer, parse_mode='html')
    message = await event.get_message()
    t = datetime.datetime.now(pytz.timezone("Asia/Tashkent"))
    time = t.strftime("%H:%M %d.%m.%Y")
    updated_message = f"{message.text}\n\n<b>Ko'rib chiqildi : </b>\n<i>Noto'g'ri raqam ❌\n\n{time}</i>"
    await message.edit(updated_message, parse_mode='html', buttons=None)
    admins = await db.get_admin()
    if admins:
        for admin in admins:
            admin_id = admin['telegram_id']
            await client.send_message(admin_id, updated_message, parse_mode="html")


@client.on(events.CallbackQuery(pattern="ok"))
async def ok(event):
    message = await event.get_message()
    t = datetime.datetime.now(pytz.timezone("Asia/Tashkent"))
    time = t.strftime("%H:%M %d.%m.%Y")
    updated_message = f"{message.text}\n\n<b>Ko'rib chiqildi </b>✅\n\n<i>{time}</i>"
    await message.edit(updated_message, parse_mode='html', buttons=None)
    admins = await db.get_admin()
    if admins:
        for admin in admins:
            admin_id = admin['telegram_id']
            await client.send_message(admin_id, updated_message, parse_mode="html")

@client.on(events.CallbackQuery(pattern="номер_ошибки+"))
async def xato_raqam(event):
    id = int(event.data.decode('utf-8').split(':')[1])
    answer = (
        "<b>Мы не смогли связаться с вами по указанному номеру.\n\n"
        "Пожалуйста, укажите номер, по которому мы сможем с вами связаться❗️</b>"
    )
    await client.send_message(id, answer, parse_mode='html')
    message = await event.get_message()
    t = datetime.datetime.now(pytz.timezone("Asia/Tashkent"))
    time = t.strftime("%H:%M %d.%m.%Y")
    updated_message = f"{message.text}\n\n<b>Рассмотрено:</b>\n<i>Неверный номер ❌\n\n{time}</i>"
    await message.edit(updated_message, parse_mode='html', buttons=None)
    admins = await db.get_admin()
    if admins:
        for admin in admins:
            admin_id = admin['telegram_id']
            await client.send_message(admin_id, updated_message, parse_mode="html")


@client.on(events.CallbackQuery(pattern="data"))
async def ok(event):
    message = await event.get_message()
    t = datetime.datetime.now(pytz.timezone("Asia/Tashkent"))
    time = t.strftime("%H:%M %d.%m.%Y")
    updated_message = f"{message.text}\n\n<b>Рассмотрено</b> ✅\n\n<i>{time}</i>"
    await message.edit(updated_message, parse_mode='html', buttons=None)
    admins = await db.get_admin()
    if admins:
        for admin in admins:
            admin_id = admin['telegram_id']
            await client.send_message(admin_id, updated_message, parse_mode="html")
