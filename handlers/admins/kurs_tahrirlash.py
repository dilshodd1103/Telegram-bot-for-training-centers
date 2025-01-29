from telethon import events

from handlers.admins.kurs_qushish import save_course_image
from handlers.users.kurslar import get_course_image_path
from keyboards.default.admin_menu import admin
from keyboards.default.kurs_tahrirlash import kurs_tahriri
from keyboards.inline.kurs_tahrirlash import course
from loader import client, db, temp


async def is_user_admin(user_id: int) -> bool:
    """Adminlikni tekshiruvchi yordamchi funksiya"""
    return await db.check_admin(selected_data=user_id)


@client.on(events.NewMessage(pattern="Kursni tahrirlash"))
async def edit_course(event):
    user_id = event.sender_id
    if await is_user_admin(user_id):
        courses = await db.select_all_kurs()
        if courses:
            temp[user_id] = {"state": "edit_kurs"}
            await event.respond("<b>Tahrirlamoqchi bo'lgan kursni tanlang:</b>", buttons=course(courses),
                                parse_mode='html')
        else:
            await event.respond("<b>Kurslar mavjud emas</b>", parse_mode='html')


@client.on(events.CallbackQuery(pattern="courses_(\d+)"))
async def select_course(event):
    user_id = event.sender_id
    if temp.get(user_id, {}).get("state") == "edit_kurs":
        course_ids = int(event.data_match.group(1))
        kurs = await db.select_kurs(course_ids)
        if kurs:
            await event.respond("<b>Qaysi ma'lumotni tahrirlamoqchisiz?</b>", buttons=kurs_tahriri, parse_mode='html')
            temp[user_id] = {"state": "edit_option", "course_id": course_ids}
        else:
            await event.respond("<b>Kurs topilmadi!</b>", parse_mode='html')


@client.on(events.NewMessage(pattern="Kurs nomini"))
async def edit_name(event):
    user_id = event.sender_id
    if temp.get(user_id, {}).get("state") == "edit_option":
        course_ids = temp[user_id]["course_id"]
        kurs = await db.select_kurs(course_ids)
        await event.respond(
            f"<b>Eski nom:</b> {kurs[1]}\n<b>Yangi nomni yuboring:</b>", parse_mode='html')
        temp[user_id]["state"] = "edit_course_name"


@client.on(events.NewMessage())
async def update_name(event):
    user_id = event.sender_id
    if temp.get(user_id, {}).get("state") == "edit_course_name":
        if event.text == "Kurs nomini":
            return
        course_ids = temp[user_id]["course_id"]
        await db.update_course_name(course_ids, event.text)
        await event.respond("<b>Kurs nomi muvaffaqiyatli o'zgartirildi ✅</b>", buttons=kurs_tahriri, parse_mode='html')
        temp[user_id]["state"] = "edit_option"


@client.on(events.NewMessage(pattern="Kurs tarifini"))
async def edit_description(event):
    user_id = event.sender_id
    if temp.get(user_id, {}).get("state") == "edit_option":
        course_ids = temp[user_id]["course_id"]
        kurs = await db.select_kurs(course_ids)
        await event.respond(
            f"<b>Eski tarif:</b> {kurs[2]}\n<b>Yangi tarifni yuboring:</b>", parse_mode='html')
        temp[user_id]["state"] = "edit_description"


@client.on(events.NewMessage())
async def update_description(event):
    user_id = event.sender_id
    if temp.get(user_id, {}).get("state") == "edit_description":
        if event.text == "Kurs tarifini":
            return
        course_ids = temp[user_id]["course_id"]
        await db.update_tarif(course_ids, event.text)
        await event.respond("<b>Kurs tarifi muvaffaqiyatli o'zgartirildi ✅</b>", buttons=kurs_tahriri,
                            parse_mode='html')
        temp[user_id]["state"] = "edit_option"


@client.on(events.NewMessage(pattern="Kurs rasmini"))
async def edit_image(event):
    user_id = event.sender_id
    if temp.get(user_id, {}).get("state") == "edit_option":
        course_ids = temp[user_id]["course_id"]
        data_int = await db.get_image(course_ids)
        kurs = await db.select_kurs(course_ids)
        if kurs[3]:
            saved_image_path = await get_course_image_path(course_id=data_int)
            await client.send_file(event.chat_id, saved_image_path, caption="<b>Eski rasm:</b>", parse_mode='html')
        await event.respond("<b>Kurs uchun yangi rasm yuboring:</b>", parse_mode='html')
        temp[user_id]["state"] = "edit_image"


@client.on(events.NewMessage())
async def update_image(event):
    user_id = event.sender_id
    if temp.get(user_id, {}).get("state") == "edit_image":
        if event.text == "Kurs rasmini":
            return

        photo = None
        if event.photo:  # Agar rasm bo'lsa
            photo = event.photo
        elif event.document and event.document.mime_type.startswith("image/"):  # Agar hujjat bo'lsa
            photo = event.document

        if photo:
            try:
                foto_id = str(photo.id)
                photo_id = await save_course_image(course_id=foto_id, photo=photo)
                course_ids = temp[user_id].get("course_id")
                await db.update_course_image(course_ids, photo_id)
                await event.respond(
                    "<b>Kurs rasmi muvaffaqiyatli o'zgartirildi ✅</b>",
                    buttons=kurs_tahriri,
                    parse_mode="html"
                )
                temp[user_id]["state"] = "edit_option"
            except Exception as e:
                await event.respond(f"Xatolik yuz berdi: {e}")
        else:
            await event.respond("Iltimos, rasm yoki rasmli fayl yuboring!")


@client.on(events.NewMessage())
async def update_image(event):
    user_id = event.sender_id

    # Foydalanuvchi holatini tekshirish
    if temp.get(user_id, {}).get("state") == "edit_image":
        if event.text == "Kurs rasmini":
            return

        # Rasmni aniqlash
        if event.photo:
            # Agar rasm photo bo'lsa
            foto_id = event.photo.id
            photo_file = await event.download_media()
        elif event.document and event.document.mime_type.startswith("image/"):
            # Agar rasm document ko'rinishida yuborilgan bo'lsa
            foto_id = event.document.id
            photo_file = await event.download_media()
        else:
            # Foydalanuvchi noto'g'ri format yuborganida xabar
            await event.respond(
                "<b>Iltimos, rasmni png yoki jpg formatida yuboring 📷</b>",
                parse_mode="html"
            )
            return

        # Rasmni saqlash
        photo_id = await save_course_image(course_id=foto_id, photo=photo_file)

        # Kursni yangilash
        course_ids = temp[user_id].get("course_id")
        await db.update_course_image(course_ids, photo_id)

        # Foydalanuvchiga javob
        await event.respond(
            "<b>Kurs rasmi muvaffaqiyatli o'zgartirildi ✅</b>",
            buttons=kurs_tahriri,
            parse_mode="html"
        )

        # Holatni yangilash
        temp[user_id]["state"] = "edit_option"


@client.on(events.NewMessage(pattern="◀️Ortga"))
async def back_to_admin(event):
    user_id = event.sender_id
    temp.pop(user_id, None)
    await event.respond("Admin menu", buttons=admin)
