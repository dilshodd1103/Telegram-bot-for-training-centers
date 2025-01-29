from datetime import datetime

from telethon import events

from keyboards.default import menu, til
from keyboards.default.contact import contact_ru, contact_uz
from keyboards.default.menu import menu_ru
from loader import client, db, temp


@client.on(events.NewMessage(pattern='/start'))
async def bot_start(event):
    user = await db.select_user(event.sender_id)

    if user is None:
        await event.respond(
            "<b>\n\nAssalomu alaykum! <i>Foreach Education</i> o'quv markazining telegram botiga xush kelibsiz!</b>\n"
            "<b>\nIltimos, tilni tanlang:</b>"
            "<b>\n\nЗдравствуйте! Добро пожаловать в телеграм-бот <i>Foreach Education</i>!</b>\n"
            "<b>\nПожалуйста, выберите язык:</b>",
            buttons=til.til,
            parse_mode='html')
        temp[event.sender_id] = {"state": "choose_language"}
    else:
        language = user[5]
        if language == "🇺🇿 O'zbekcha":
            await event.respond(
                f"<b>Assalomu alaykum <i>{event.sender.first_name}</i></b>",
                parse_mode='html'
            )
            await event.respond("<i>📋Menu:</i>", buttons=menu, parse_mode='html')
        else:
            await event.respond(
                f"<b>Здравствуйте <i>{event.sender.first_name}</i></b>",
                parse_mode='html'
            )
            await event.respond("<i>📋Меню:</i>", buttons=menu_ru, parse_mode='html')


@client.on(events.NewMessage(func=lambda e: e.text in ["🇺🇿 O'zbekcha", "🇷🇺 Русский"]))
async def choose_language(event):
    user_id = event.sender_id
    if temp.get(user_id, {}).get("state") == "choose_language":
        language = event.text.strip()
        temp[user_id] = {'language': language, 'state': 'name_start'}

        if language == "🇺🇿 O'zbekcha":
            await event.respond("<b>Ism-familiyangizni yuboring : </b>", parse_mode='html')
        else:
            await event.respond("<b>Пожалуйста, отправьте ваше имя и фамилию:</b>", parse_mode='html')


@client.on(events.NewMessage())
async def set_name(event):
    user_id = event.sender_id
    state = temp.get(user_id, {}).get("state")

    if state == "choose_language" or event.text in ["🇺🇿 O'zbekcha", "🇷🇺 Русский"]:
        return

    if state == "name_start":
        temp[user_id]["name"] = event.text.strip()
        language = temp[user_id].get("language", "🇺🇿 O'zbekcha")

        if language == "🇺🇿 O'zbekcha":
            await event.respond("<b>Raqamingizni yuboring : </b>", buttons=contact_uz, parse_mode='html')
        else:
            await event.respond("<b>Пожалуйста, отправьте ваш номер телефона:</b>", buttons=contact_ru,
                                parse_mode='html')

        temp[user_id]["state"] = "phone_start"


@client.on(events.NewMessage(func=lambda e: e.contact and temp.get(e.sender_id, {}).get('state') == 'phone_start'))
async def contact_user(event):
    user_id = event.sender_id
    raqam = event.contact.phone_number
    state_data = temp.get(user_id, {})

    language = state_data.get('language', 'uz')
    if raqam.startswith("+998"):
        state_data['phone_number'] = raqam
    elif raqam.startswith("998"):
        state_data['phone_number'] = f"+{raqam}"
    else:
        if language == "🇺🇿 O'zbekcha":
            await event.respond(
                "<b>Xato telefon raqami ❗\n\n<i>Iltimos raqamingizni qayta yuboring.</i></b>", parse_mode='html'
            )
        else:
            await event.respond(
                "<b>Неверный номер телефона ❗\n\n<i>Пожалуйста, отправьте правильный номер.</i></b>", parse_mode='html'
            )
        return

    user_data = state_data

    await db.add_user(
        telegram_id=event.sender_id,
        username=event.sender.first_name,
        full_name=user_data['name'],
        language=user_data['language'],
        phone_num=user_data['phone_number'],
        admin=False,
        joined_at=datetime.now()
    )

    if language == "🇺🇿 O'zbekcha":
        await event.respond("<b>Raqamingiz muvaffaqiyatli qabul qilindi ✅</b>", parse_mode='html')
        await event.respond("<b><i>📋Menu:</i></b>", buttons=menu.menu, parse_mode='html')
    else:
        await event.respond("<b>Ваш номер успешно принят ✅</b>", parse_mode='html')
        await event.respond("<b><i>📋Меню:</i></b>", buttons=menu.menu_ru, parse_mode='html')

    count = await db.count_users()
    data = count if count is not None else 0
    notify_msg = (
        f"{event.sender.first_name} bazaga qo'shildi.\nBazada {data} ta foydalanuvchi bor.")
    admins = await db.get_admin()
    if admins:
        for admin in admins:
            admin_id = admin['telegram_id']
            await client.send_message(admin_id, notify_msg, parse_mode='html')

    temp.pop(event.sender_id, None)
