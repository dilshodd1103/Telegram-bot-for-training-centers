from telethon import events

from keyboards.default.bekor_qilish import bekor6, bekor6_ru
from keyboards.default.contact import contact2, contact2_ru
from keyboards.default.menu import menu, menu_ru
from keyboards.default.sozlama_keyboards import sozlama, sozlama_ru
from keyboards.default.til import til2, til2_ru
from loader import client, db, temp


@client.on(events.NewMessage(pattern="🛠Sozlamalar"))
async def sozlamalar(event):
    user_id = event.sender_id
    user = await db.select_user(user_id)
    await event.respond(
        f"\n👤 Ismingiz :    {user[2]}\n☎️ Telefon raqamingiz : {user[3]}\n🖇 Joriy til :    {user[5]}",
        buttons=sozlama, parse_mode='html')
    temp[user_id] = {"state": "sozlamalar"}


@client.on(events.NewMessage(pattern="◀️  Ortga"))
async def back_menu(event):
    user_id = event.sender_id
    if temp.get(user_id, {}).get("state") == "sozlamalar":
        await event.respond("Menu", buttons=menu)
        temp.pop(user_id, None)


@client.on(events.NewMessage(pattern="♻️Ismni o'zgartirish"))
async def edit_name(event):
    user_id = event.sender_id
    if temp.get(user_id, {}).get("state") == "sozlamalar":
        await event.respond("Yangi ism yuboring:", buttons=bekor6)
        temp[user_id] = {'state': 'edit_name'}


@client.on(events.NewMessage())
async def edit_name_edit(event):
    user_id = event.sender_id
    if temp.get(user_id, {}).get("state") == "edit_name":
        if event.text == "♻️Ismni o'zgartirish":
            return
        ism = event.text.strip()
        if ism == "⬅️Orqaga":
            await event.respond("Sozlamalar", buttons=sozlama)
            temp[user_id] = {'state': 'sozlamalar'}
            return
        if not ism:
            await event.reply("Iltimos, ism kiriting:")
            return
        if 2 < len(ism) < 100:
            await db.update_user_name(ism, user_id)
            await event.respond("Ismingiz muvaffaqiyatli o'zgartirildi ✅", buttons=sozlama)
            temp[user_id] = {'state': 'sozlamalar'}
        else:
            await event.reply("Ism uzunligi noto'g'ri, qayta kiriting:")


@client.on(events.NewMessage(pattern="🔢Raqamni o'zgartirish"))
async def edit_phone(event):
    user_id = event.sender_id
    if temp.get(user_id, {}).get("state") == "sozlamalar":
        await event.respond(
            "Raqamingizni yuboring:\n+998901234567 ko'rinishida yoki '🔢Raqamimni yuborish' tugmasini bosing.",
            buttons=contact2)
        temp[user_id] = {'state': 'raqam2'}


@client.on(events.NewMessage())
async def edit_phone_edit(event):
    user_id = event.sender_id
    if temp.get(user_id, {}).get("state") == "raqam2":
        if event.text == "🔢Raqamni o'zgartirish":
            return
        raqam = event.text.strip()
        if raqam == "⏪Ortga":
            await event.respond("Sozlamalar", buttons=sozlama)
            temp[user_id] = {'state': 'sozlamalar'}
            return
        if event.contact:
            raqam = event.contact.phone_number
        else:
            raqam = event.text.strip()

        if raqam.startswith("+998") and len(raqam) == 13:
            await db.update_user_number(user_id, raqam)
            await event.respond("Raqamingiz muvaffaqiyatli o'zgartirildi ✅", buttons=sozlama)
            temp[user_id] = {'state': 'sozlamalar'}
        else:
            await event.reply("Xato telefon raqami. Qayta yuboring!")


@client.on(events.NewMessage(pattern="🔄Tilni almashtirish"))
async def edit_language(event):
    user_id = event.sender_id
    if temp.get(user_id, {}).get("state") == "sozlamalar":
        await event.respond("Iltimos, tilni tanlang:", buttons=til2)
        temp[user_id] = {'state': 'edit_language'}


@client.on(events.NewMessage())
async def edit_language_edit(event):
    user_id = event.sender_id
    if temp.get(user_id, {}).get('state') == 'edit_language':
        if event.text == "🔄Tilni almashtirish":
            return
        til = event.text.strip()
        if til == "◀Ortga":
            await event.respond("Sozlamalar", buttons=sozlama)
            temp[user_id] = {'state': 'sozlamalar'}
        elif til == "🇺🇿 O'zbekcha":
            await db.update_language(user_id, til)
            await event.respond("Til muvaffaqiyatli O'zbekchaga o'zgartirildi ✅", buttons=sozlama)
            temp[user_id] = {'state': 'sozlamalar'}
        elif til == "🇷🇺 Русский":
            await db.update_language(user_id, til)
            await event.respond("Язык успешно изменен на Русский ✅", buttons=sozlama_ru)
            temp[user_id] = {'state': 'sozlamalar_'}
        else:
            await event.respond("Iltimos, tugmalardan birini tanlang!")


@client.on(events.NewMessage(pattern="🛠Настройки"))
async def sozlamalar(event):
    user_id = event.sender_id
    user = await db.select_user(user_id)
    await event.respond(
        f"\n👤 Ваше имя: {user[2]}\n☎️ Ваш номер телефона: {user[3]}\n🖇 Текущий язык: {user[5]}",
        buttons=sozlama_ru, parse_mode='html')
    temp[user_id] = {"state": "sozlamalar_"}


@client.on(events.NewMessage(pattern="◀️ Назад"))
async def back_menu(event):
    user_id = event.sender_id
    if temp.get(user_id, {}).get("state") == "sozlamalar_":
        await event.respond("Меню", buttons=menu_ru)
        temp.pop(user_id, None)


@client.on(events.NewMessage(pattern="♻️Изменить имя"))
async def edit_name(event):
    user_id = event.sender_id
    if temp.get(user_id, {}).get("state") == "sozlamalar_":
        await event.respond("Отправьте новое имя:", buttons=bekor6_ru)
        temp[user_id] = {'state': 'edit_name_'}


@client.on(events.NewMessage())
async def edit_name_edit(event):
    user_id = event.sender_id
    if temp.get(user_id, {}).get("state") == "edit_name_":
        if event.text == "♻️Изменить имя":
            return
        ism = event.text.strip()
        if ism == "⬅️Назад":
            await event.respond("Настройки", buttons=sozlama_ru)
            temp[user_id] = {'state': 'sozlamalar_'}
            return
        if not ism:
            await event.reply("Пожалуйста, введите имя:")
            return
        if 2 < len(ism) < 100:
            await db.update_user_name(ism, user_id)
            await event.respond("Ваше имя успешно изменено ✅", buttons=sozlama_ru)
            temp[user_id] = {'state': 'sozlamalar_'}
        else:
            await event.reply("Неверная длина имени, введите снова:")


@client.on(events.NewMessage(pattern="🔢Изменить номер"))
async def edit_phone(event):
    user_id = event.sender_id
    if temp.get(user_id, {}).get("state") == "sozlamalar_":
        await event.respond(
            "Отправьте ваш номер телефона:\nВ формате +998901234567 или нажмите на '🔢Отправить мой номер'.",
            buttons=contact2_ru)
        temp[user_id] = {'state': 'raqam2_'}


@client.on(events.NewMessage())
async def edit_phone_edit(event):
    user_id = event.sender_id
    if temp.get(user_id, {}).get("state") == "raqam2_":
        if event.text == "🔢Изменить номер":
            return
        raqam = event.text.strip()
        if raqam == "⏪Назад":
            await event.respond("Настройки", buttons=sozlama_ru)
            temp[user_id] = {'state': 'sozlamalar_'}
            return
        if event.contact:
            raqam = event.contact.phone_number
        else:
            raqam = event.text.strip()

        if raqam.startswith("+998") and len(raqam) == 13:
            await db.update_user_number(user_id, raqam)
            await event.respond("Ваш номер успешно изменен ✅", buttons=sozlama_ru)
            temp[user_id] = {'state': 'sozlamalar_'}
        else:
            await event.reply("Неправильный номер телефона. Отправьте снова!")


@client.on(events.NewMessage(pattern="🔄Сменить язык"))
async def edit_language(event):
    user_id = event.sender_id
    if temp.get(user_id, {}).get("state") == "sozlamalar_":
        await event.respond("Пожалуйста, выберите язык:", buttons=til2_ru)
        temp[user_id] = {'state': 'edit_language_'}


@client.on(events.NewMessage())
async def edit_language_edit(event):
    user_id = event.sender_id
    if temp.get(user_id, {}).get('state') == 'edit_language_':
        if event.text == "🔄Сменить язык":
            return
        til = event.text.strip()
        if til == "◀Назад":
            await event.respond("Настройки", buttons=sozlama_ru)
            temp[user_id] = {'state': 'sozlamalar_'}
        elif til == "🇺🇿 O'zbekcha":
            await db.update_language(user_id, til)
            await event.respond("Язык успешно изменен на O'zbekcha ✅", buttons=sozlama)
            temp[user_id] = {'state': 'sozlamalar'}
        elif til == "🇷🇺 Русский":
            await db.update_language(user_id, til)
            await event.respond("Язык успешно изменен на Русский ✅", buttons=sozlama_ru)
            temp[user_id] = {'state': 'sozlamalar_'}
        else:
            await event.respond("Пожалуйста, выберите один из предложенных вариантов!")
