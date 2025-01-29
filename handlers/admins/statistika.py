from telethon import events
from telethon.tl.custom import Button
from loader import client, db
import pytz


async def is_user_admin(user_id: int) -> bool:
    """Adminlikni tekshiruvchi yordamchi funksiya"""
    return await db.check_admin(selected_data=user_id)


@client.on(events.NewMessage(pattern="Statistika"))
async def bot_statistic(event):
    if await is_user_admin(event.sender_id):
        user = await db.count_users()
        start_user = await db.add_month()
        # latest_news_reader = await db.latest_news_reader()
        active_user = await db.get_active_users()
        await db.add_statistic(all_subscribers=user, for_last_month=start_user)
        result = (f"<b>Obunachilar soni: <i>{user} ta</i>\n\nOxirgi oyda qo'shilganlar: <i>{start_user} ta</i>"
                  f"\n\n24 soat ichida botdan foydalanganlar: <i>{active_user} ta</i></b>")
        await event.respond(result, parse_mode="html")


@client.on(events.NewMessage(pattern="Ma'lumotlar"))
async def is_admin(event):
    if await is_user_admin(event.sender_id):
        data = await db.count_admins()
        message = await db.get_message()
        await db.add_informations(data, message)
        if message:
            sent_date = message.astimezone(pytz.timezone('Asia/Tashkent'))
            formatted_date = sent_date.strftime("%d-%m-%Y %H:%M:%S")
            await event.respond(
                f"<b>Botdagi Adminlar soni: <i>{data}</i> ta\n\n"
                f"Eng oxirgi jo'natilgan xabar: {formatted_date}</b>",
                parse_mode="html"
            )
