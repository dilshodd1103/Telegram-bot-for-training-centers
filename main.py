import asyncio
from loader import client, db
import handlers, middlewares, filters


async def main():
    await db.create()
    await client.start()

    message = "Bot is running!"
    print(message)
    admins = await db.get_admin()
    if admins:
        for admin in admins:
            admin_id = admin['telegram_id']
            try:
                await client.send_message(admin_id, message)
                print(f"Message sent to admin {admin_id}")
            except Exception as e:
                print(f"Failed to send message to {admin_id}: {e}")

    try:
        await client.run_until_disconnected()
    except asyncio.CancelledError:
        print("Main task cancelled.")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
