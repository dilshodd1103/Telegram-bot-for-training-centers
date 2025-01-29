from pathlib import Path

from PIL import Image
from telethon import events
from telethon.tl.types import Photo, Document

from keyboards.default.admin_menu import admin
from keyboards.default.bekor_qilish import bekor, bekor3, bekor4
from keyboards.default.optimal_Buttons import optional_buttons
from loader import client, db, temp


async def is_user_admin(user_id: int) -> bool:
    """Adminlikni tekshiruvchi yordamchi funksiya"""
    return await db.check_admin(selected_data=user_id)


async def save_course_image(course_id, photo):
    media_root = Path("/home/dilshod/Projects/telegram_project/app/foreach_django/media")
    course_folder = media_root / "rasmlar"
    course_folder.mkdir(parents=True, exist_ok=True)


    if isinstance(photo, Photo):
        file_extension = 'png'
    elif isinstance(photo, Document) and photo.mime_type and 'image' in photo.mime_type:
        file_extension = photo.mime_type.split('/')[-1].lower()
    else:
        raise ValueError("Rasm yoki fayl yuborish kerak!")

    file_name = f"{course_id}.{file_extension}"
    file_path = course_folder / file_name

    try:
        file = await client.download_media(photo, file_path)
        if file_extension != 'png':
            with Image.open(file_path) as img:
                jpg_file_path = course_folder / f"{course_id}.png"
                img.convert('RGB').save(jpg_file_path, 'JPEG')
                file_path.unlink()
    except Exception as e:
        print(f"Rasm yuklashda xato: {e}")
        raise

    return str(f"rasmlar/{course_id}.png")


@client.on(events.NewMessage(pattern="Kurs qo'shish"))
async def add_kurs(event):
    user_id = event.sender_id
    if await is_user_admin(user_id):
        await event.respond("<b>Kurs nomini yuboring :</b>", buttons=bekor3, parse_mode='html')
        temp[user_id] = {"state": "kurs_nomi"}


@client.on(events.NewMessage())
async def handle_states(event):
    user_id = event.sender_id
    message = event.message.message
    state = temp.get(user_id, {}).get("state")
    if event.text == "Kurs qo'shish":
        return
    if state == "kurs_nomi":
        if message == 'Orqaga':
            temp.pop(user_id, None)
            await event.respond("Admin_menu", buttons=admin)
        elif len(message) < 255:
            temp[user_id]["kurs_nomi"] = message
            temp[user_id]["state"] = "kurs_rasm"
            await event.respond(
                "<b>Kurs uchun rasmni yuboring yoki “⬇️O‘tkazib yuborish” tugmasini bosing:</b>",
                parse_mode="html",
                buttons=optional_buttons,
            )
        else:
            await event.respond("<b>Juda uzun, qayta kiriting (255 ta belgi):</b>", buttons=bekor, parse_mode='html')


    elif state == "kurs_rasm":
        if message == "⬇️O‘tkazib yuborish":
            temp[user_id]["state"] = "kurs_tarif"
            await event.respond("<b>Kurs ta'rifini yuboring:</b>", buttons=bekor4, parse_mode='html')
        elif message == '⬅️Ortga':
            temp[user_id]["state"] = "kurs_nomi"
            await event.respond("<b>Kurs nomini yuboring :</b>", buttons=bekor3, parse_mode='html')
        elif event.photo:
            file_id = event.photo.id
            saved_image_path = await save_course_image(course_id=file_id, photo=event.photo)
            temp[user_id]["kurs_rasm"] = saved_image_path
            temp[user_id]["state"] = "kurs_tarif"
            await event.respond("<b>Kurs ta'rifini yuboring:</b>", buttons=bekor4, parse_mode='html')
        elif event.document:
            file_id = event.document.id
            saved_image_path = await save_course_image(course_id=file_id, photo=event.document)
            temp[user_id]["kurs_rasm"] = saved_image_path
            temp[user_id]["state"] = "kurs_tarif"
            await event.respond("<b>Kurs ta'rifini yuboring:</b>", buttons=bekor4, parse_mode='html')
        else:
            await event.respond("<b>Faqatgina rasm yoki fayl yuboring yoki o'tkazib yuboring:</b>",
                                buttons=optional_buttons, parse_mode='html')

    elif state == "kurs_tarif":
        kurs_data = temp.get(user_id, {})
        kurs_nomi = kurs_data.get("kurs_nomi")
        kurs_rasm = kurs_data.get("kurs_rasm")

        if message == "Rasm yuklash":
            temp[user_id]["state"] = "kurs_rasm"
            await event.respond("<b>Kurs uchun rasmni yuboring yoki “⬇️O‘tkazib yuborish” tugmasini bosing:</b>",
                                parse_mode="html", buttons=optional_buttons)
        elif kurs_nomi:
            await db.add_kurs(kurs_nomi, message, kurs_rasm)
            await event.respond("<b>Kurs muvaffaqiyatli qo'shildi ✅</b>", buttons=admin, parse_mode='html')
            temp.pop(user_id, None)
