def adminlar(listt, page=1, row_width=2):
    kurs = []
    start_index = (page - 1) * 50
    end_index = start_index + 50
    page_users = listt[start_index:end_index]
    row = []
    for kurs1 in page_users:
        row.append(Button.inline(text=kurs1[1], data=f"set_{kurs1[0]}"))

        if len(row) == row_width:
            kurs.append(row)
            row = []

    if row:
        kurs.append(row)

    navigation_buttons = []
    if page > 1:
        navigation_buttons.append(Button.inline(text="⬅️ Orqaga", data=f"page_{page - 1}"))

    if end_index < len(listt):
        navigation_buttons.append(Button.inline(text="➡️ Keyingi", data=f"page_{page + 1}"))
    else:
        navigation_buttons.append(Button.inline(text="🔙Ortga", data="back1"))

    if navigation_buttons:
        kurs.append(navigation_buttons)

    return kurs

from telethon.tl.custom import Button

def admin_list_keyboard(admins):
    """Adminlarni ko'rsatish uchun klaviatura"""
    keyboard = []

    # Adminlar ro'yxatini klaviaturaga qo'shish
    for admin in admins:
        keyboard.append([
            Button.inline(
                f"ID: {admin['id']}   {admin['username']}",
                b"remove_admin_" + str(admin['id']).encode()
            )
        ])

    # Oxirida "Ortga" tugmasini qo'shish
    keyboard.append([Button.inline("◀️ Ortga", b"qaytish")])

    return keyboard
