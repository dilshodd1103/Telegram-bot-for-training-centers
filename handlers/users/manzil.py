from telethon import events
from loader import client, db


@client.on(events.NewMessage(pattern="📍Manzilimiz"))
async def manzil(event):
    user_id = event.sender_id
    await event.respond("<b>🏢 Qarshi shahar, </b>", parse_mode="html")
    await db.save_user_action(user_id)


@client.on(events.NewMessage(pattern="🔗Biz bilan bog'lanish"))
async def boglan(event):
    user_id = event.sender_id
    await event.respond(
        "<b>Murojaat uchun telefon raqamlari :\n\n☎️+998940500093\n☎️+998946389778</b>",
        parse_mode="html"
    )
    await db.save_user_action(user_id)


@client.on(events.NewMessage(pattern="📍Наш адрес"))
async def manzil(event):
    user_id = event.sender_id
    await event.respond("<b>🏢 Город Карши, </b>", parse_mode="html")
    await db.save_user_action(user_id)


@client.on(events.NewMessage(pattern="🔗Связаться с нами"))
async def boglan(event):
    user_id = event.sender_id
    await event.respond(
        "<b>Телефонные номера для обращения:\n\n☎️+998940500093\n☎️+998946389778</b>",
        parse_mode="html"
    )
    await db.save_user_action(user_id)
