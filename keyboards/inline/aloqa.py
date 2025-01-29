from telethon.tl.custom import Button

def aloqa(call):
    keyboard = [
        [Button.inline("📱Aloqaga chiqish", data=call)]
    ]
    return keyboard

def aloqa_ru(call):
    keyboard = [
        [Button.inline("📱Свяжитесь с нами", data=call)]
    ]
    return keyboard
