from telethon.tl.custom import Button


def reklama_user_keyboard(users, selected_users):
    """Foydalanuvchilarni tanlash va yuborish tugmalari"""
    if isinstance(selected_users, int):
        selected_users = [selected_users]

    keyboard = []
    for user in users:
        user_id = user['telegram_id']
        username = user['username']

        if user_id in selected_users:
            button_text = f"✅ {username}"
        else:
            button_text = username

        keyboard.append([Button.inline(button_text, data=f"user_{user_id}")])

    keyboard.append([
        Button.inline("✅ Yuborish", data="send"),
        Button.inline("◀️ Ortga", data="cancel")
    ])

    return keyboard
