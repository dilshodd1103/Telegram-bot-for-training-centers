from telethon import events
import re
from keyboards.default.menu import menu, menu_ru
from keyboards.inline.aloqa import aloqa, aloqa_ru
from keyboards.inline.aloqaga_chiq import aloqa_keyboard, aloqa_keyboard_ru
from keyboards.inline.kurslar import user_and_course, user_and_course_ru
from loader import client, db

client.state = None

from pathlib import Path


async def get_course_image_path(course_id):
    media_root = Path("/home/dilshod/Projects/telegram_project/app/foreach_django/media")
    file_name = f"{course_id}"
    file_path = media_root / file_name
    if not file_path.exists():
        raise FileNotFoundError(f"Rasm {file_path} topilmadi!")
    return str(file_path)


@client.on(events.NewMessage(pattern="📚Bizning kurslarimiz"))
async def kurss(event):
    client.state = "VIEW_COURSES"
    course = await db.select_all_kurs()
    if course:
        await event.respond(
            f"<b><b>📚Kurslarimiz soni : </b><i>{len(course)} ta</i>", parse_mode="html"
        )
        await event.respond(
            "<b><b>📚Bizning kurslarimiz : </b>",
            buttons=user_and_course(course),
            parse_mode="html",
        )
        client.kurslar_state = True
    else:
        await event.respond("<b>Kurslar mavjud emas</b>", parse_mode="html")


@client.on(events.CallbackQuery(pattern="back3"))
async def menuu(event):
    client.state = "BACK_TO_MENU"
    await event.respond("<i>Menu : </i>", buttons=menu, parse_mode="html")
    user_id = event.sender_id
    await db.save_user_action(user_id)
    client.kurslar_state = False


@client.on(events.CallbackQuery())
async def tarif(event):
    if event.data.isdigit() and getattr(client, "kurslar_state", False):
        client.state = "VIEW_COURSE_DETAILS"
        data = int(event.data)
        data_img = await db.get_image(data)
        kurs = await db.select_kurs(data)
        user = await db.select_user(event.sender_id)
        kurs_nomi, tarif, rasm = kurs[2], kurs[5], kurs[7]

        if rasm:
            saved_image_path = await get_course_image_path(course_id=data_img)
            await client.send_file(
                event.sender_id,
                saved_image_path,
                caption=f"<b>📕Kurs nomi: {kurs_nomi}</b>\n\n{tarif}",
                parse_mode="html",
            )
        else:
            await event.respond(
                f"<b>📕Kurs nomi: {kurs_nomi}</b>\n\n{tarif}", parse_mode="html"
            )
        answer = (
            f"<i>📕Kurs haqida qo'shimcha ma'lumot olishni istasangiz, operatorimiz siz bilan bog'lanishi mumkin.\n"
            f"Buning uchun quyidagi tugmani bosing :\n\n"
            f"*Sizning raqamingiz : <u>{user[3]}</u>, boshqa raqamga qo'ng'iroq qilishimizni xohlasangiz "
            f" \n<i>🛠Sozlamalar</i> bo'limidan raqamingizni o'zgartiring.</i>"
        )
        await event.respond(
            answer, buttons=aloqa(f"aloqa:{kurs_nomi}"), parse_mode="html"
        )
        await event.respond("<i>Menu : </i>", buttons=menu, parse_mode="html")

        user_id = event.sender_id
        await db.save_user_action(user_id)
        client.kurslar_state = False


@client.on(events.CallbackQuery(pattern="aloqa:+"))
async def aloqa1(event):
    client.state = "REQUEST_CONTACT"
    kurs = event.data.decode("utf-8").split(":")[1]
    user = await db.select_user(event.sender_id)
    username = event.sender.username or "Username mavjud emas"
    if username != "Username mavjud emas":
        username = f"@{username}"

    answer = (
        f"<b>Foydalanuvchi <u>{user[1]}</u>  <u>{kurs}</u> kursi uchun aloqaga chiqishni so'radi\n\n"
        f"Telefon raqam : <i>{user[3]}</i>\nUsername : <i>{username}</i></b>"
    )

    await event.respond(
        f"<b><i>{kurs}</i> kursi bo'yicha so'rovingiz yuborildi✅\n\n"
        f"<i>Operatorlarimiz tez orada <u>{user[3]}</u> raqamingizga aloqaga chiqishadi.</i></b>",
        parse_mode="html",
    )

    client.state = "NOTIFY_ADMINS"
    admins = await db.get_admin()
    if admins:
        for admin in admins:
            admin_id = admin["telegram_id"]
            await client.send_message(
                admin_id,
                answer,
                buttons=aloqa_keyboard(event.sender_id),
                parse_mode="html",
            )


client.state = None


@client.on(events.NewMessage(pattern="📚Наши курсы"))
async def kurss(event):
    client.state = "VIEW_COURSES_"
    course = await db.select_all_kurs()
    if course:
        await event.respond(
            f"<b><b>📚Количество курсов: </b><i>{len(course)} шт</i>", parse_mode="html"
        )
        await event.respond(
            "<b><b>📚Наши курсы: </b>",
            buttons=user_and_course_ru(course),
            parse_mode="html",
        )
        client.kurslar_state = True
    else:
        await event.respond("<b>Курсы отсутствуют</b>", parse_mode="html")


@client.on(events.CallbackQuery(pattern="back4"))
async def menuu(event):
    client.state = "BACK_TO_MENU_"
    await event.respond("<i>Меню: </i>", buttons=menu_ru, parse_mode="html")
    user_id = event.sender_id
    await db.save_user_action(user_id)
    client.kurslar_state = False

@client.on(events.CallbackQuery(pattern=r"see_(\d+)"))
async def tarif(event):
    callback_data = event.data.decode('utf-8')
    match = re.match(r"see_(\d+)", callback_data)
    if match and getattr(client, "kurslar_state", False):
        client.state = "VIEW_COURSE_DETAILS_"
        data = int(match.group(1))

        data_img = await db.get_image(data)
        kurs = await db.select_kurs(data)
        user = await db.select_user(event.sender_id)
        kurs_nomi, tarif, rasm = kurs[3], kurs[6], kurs[7]

        if rasm:
            saved_image_path = await get_course_image_path(course_id=data_img)
            await client.send_file(
                event.sender_id,
                saved_image_path,
                caption=f"<b>📕Название курса: {kurs_nomi}</b>\n\n{tarif}",
                parse_mode="html")
        else:
            await event.respond(
                f"<b>📕Название курса: {kurs_nomi}</b>\n\n{tarif}", parse_mode="html")
        answer = (
            f"<i>📕Если вы хотите узнать дополнительную информацию о курсе, наш оператор свяжется с вами.\n"
            f"Для этого нажмите следующую кнопку:\n\n"
            f"*Ваш номер телефона: <u>{user[3]}</u>. Если вы хотите, чтобы мы позвонили на другой номер, "
            f"измените его в разделе <i>🛠Настройки</i>.</i>")
        await event.respond(
            answer, buttons=aloqa_ru(f"aloqa_ru:{kurs_nomi}"), parse_mode="html")
        await event.respond("<i>Меню: </i>", buttons=menu_ru, parse_mode="html")
        user_id = event.sender_id
        await db.save_user_action(user_id)
        client.kurslar_state = False
    else:
        await event.respond("Неверные данные или действие недоступно.", parse_mode="html")


@client.on(events.CallbackQuery(pattern="aloqa_ru:+"))
async def aloqa1(event):
    client.state = "REQUEST_CONTACT_"
    kurs = event.data.decode("utf-8").split(":")[1]
    user = await db.select_user(event.sender_id)
    username = event.sender.username or "Имя пользователя отсутствует"
    if username != "Имя пользователя отсутствует":
        username = f"@{username}"

    answer = (
        f"<b>Пользователь <u>{user[1]}</u> запросил связь по курсу <u>{kurs}</u>\n\n"
        f"Номер телефона: <i>{user[3]}</i>\nИмя пользователя: <i>{username}</i></b>"
    )

    await event.respond(
        f"<b><i>Ваш запрос по курсу <i>{kurs}</i> отправлен✅\n\n"
        f"<i>Наши операторы скоро свяжутся с вами по номеру <u>{user[3]}</u>.</i></b>",
        parse_mode="html",
    )

    client.state = "NOTIFY_ADMINS_"
    admins = await db.get_admin()
    if admins:
        for admin in admins:
            admin_id = admin["telegram_id"]
            await client.send_message(
                admin_id,
                answer,
                buttons=aloqa_keyboard_ru(event.sender_id),
                parse_mode="html",
            )
