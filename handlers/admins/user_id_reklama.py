import asyncio

from telethon import events

from keyboards.default.admin_menu import admin
from keyboards.default.bekor_qilish import bekor2
from keyboards.inline.user_id_reklama import reklama_user_keyboard
from loader import client, db, temp

user_data = {}


async def is_user_admin(user_id: int) -> bool:
    """Adminlikni tekshiruvchi yordamchi funksiya"""
    return await db.check_admin(selected_data=user_id)


@client.on(events.NewMessage(pattern="Alohida xabar"))
async def start_reklama(event):
    if await is_user_admin(event.sender_id):
        user_id = event.sender_id
        await event.respond(
            "<b>Yaxshi, reklama postini yuboring : </b>\n<i>(Text, Rasm, Video, Dokument)</i>\n"
            "❗️<i>Tanlangan foydalanuvchilarga yuboriladi</i>",
            buttons=bekor2,
            parse_mode="html"
        )
        temp[user_id] = {"state": "user_message"}


@client.on(events.NewMessage(pattern='Ortga'))
async def back_admin_menu(event):
    user_id = event.sender_id
    if temp.get(user_id, {}).get("state") == "user_message":
        await event.respond("Admin menu", buttons=admin)
        temp.pop(user_id, None)


@client.on(events.NewMessage())
async def save_reklama(event):
    if await is_user_admin(event.sender_id):
        user_id = event.sender_id
        if temp.get(user_id, {}).get("state") == "user_message":
            if event.text == "Alohida xabar":
                return
            user_data[event.sender_id] = {
                "content_type": event.message.media.__class__.__name__ if event.message.media else "text",
                "message_id": event.message.id,
                "chat_id": event.sender_id,
                "selected_users": []
            }

            users = await db.select_all_users()
            keyboard = reklama_user_keyboard(users, [])
            await event.respond(
                "<b>Foydalanuvchilarni tanlang yoki <i>◀️Ortga</i> tugmasini bosing:</b>",
                buttons=keyboard,
                parse_mode="html"
            )
            temp[user_id] = {'state': 'id_message'}


@client.on(events.CallbackQuery())
async def handle_user_selection(event):
    if await is_user_admin(event.sender_id):
        user_id = event.sender_id
        if temp.get(user_id, {}).get("state") == "id_message":

            data = user_data[event.sender_id]
            selected_users = data["selected_users"]

            if event.data == b"cancel":
                await event.respond("<b>Xabarni qayta yuboring yoki <i>Ortga</i> qayting tugmasini bosing.</b>", parse_mode='html')
                temp[user_id] = {'state': 'user_message'}

            elif event.data == b"send":
                if not selected_users:
                    await event.respond("<b>Hech qanday foydalanuvchi tanlanmagan!</b>", parse_mode='html')
                    return

                data = user_data[event.sender_id]
                content_type = data["content_type"]
                message_id = data["message_id"]
                from_chat_id = data["chat_id"]
                successful, failed = 0, 0

                for user_id in selected_users:
                    try:
                        message = await client.get_messages(from_chat_id, ids=message_id)
                        if content_type == "text":
                            await client.send_message(user_id, message.text)
                        else:
                            file = await message.download_media()
                            await client.send_file(user_id, file, caption=message.text)
                        successful += 1
                    except Exception as e:
                        print(f"User ID {user_id} uchun xatolik: {e}")
                        failed += 1
                    finally:
                        await asyncio.sleep(0.1)
                await event.respond(
                    f"<b>✅ Yuborildi: {successful}\n❌ Yuborilmadi: {failed}</b>",
                    buttons=admin, parse_mode="html"
                )
                temp.pop(user_id, None)


            elif event.data.decode().startswith("user_"):
                user_id = int(event.data.decode().split("_")[1])

                if user_id not in selected_users:
                    selected_users.append(user_id)
                    await event.answer("Foydalanuvchi tanlandi ✅")
                else:
                    selected_users.remove(user_id)
                    await event.answer("Foydalanuvchi olib tashlandi ❌")

                users = await db.select_all_users()
                keyboard = reklama_user_keyboard(users, selected_users)
                await event.edit(buttons=keyboard)
