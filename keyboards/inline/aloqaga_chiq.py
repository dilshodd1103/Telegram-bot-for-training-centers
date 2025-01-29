from telethon.tl.custom import Button

def aloqa_keyboard(user_id):
    keyboard_aloqa = [
        [Button.inline("Raqam ushbu foydalanuvchiga tegishli emas❌", data=f"wrong_number+:{user_id}")],
        [Button.inline("Bajarildi ✅", data="ok")]
    ]
    return keyboard_aloqa

def aloqa_keyboard_ru(user_id):
    keyboard_aloqa = [
        [Button.inline("Номер не принадлежит этому пользователю❌", data=f"номер_ошибки+:{user_id}")],
        [Button.inline("Сделанный ✅", data="data")]
    ]
    return keyboard_aloqa
