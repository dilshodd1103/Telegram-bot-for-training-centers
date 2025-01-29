from telethon.tl.custom import Button

def kurslar(listt, row_width=2):
    kurs_keyboard = []
    row = []

    for kurs1 in listt:
        row.append(Button.inline(text=kurs1[1], data=f"kurs_{kurs1[0]}"))

        if len(row) == row_width:
            kurs_keyboard.append(row)
            row = []

    if row:
        kurs_keyboard.append(row)

    kurs_keyboard.append([Button.inline(text="🔙Ortga", data="back")])
    return kurs_keyboard

def user_and_course(listt, row_width=2):
    kurs_keyboard = []
    row = []

    for kurs1 in listt:
        row.append(Button.inline(text=kurs1[1], data=f"{kurs1[0]}"))

        if len(row) == row_width:
            kurs_keyboard.append(row)
            row = []

    if row:
        kurs_keyboard.append(row)

    kurs_keyboard.append([Button.inline(text="🔙Ortga", data="back3")])
    return kurs_keyboard


def user_and_course_ru(listt, row_width=2):
    kurs_keyboard = []
    row = []

    for kurs1 in listt:
        row.append(Button.inline(text=kurs1[3], data=f"see_{kurs1[0]}"))

        if len(row) == row_width:
            kurs_keyboard.append(row)
            row = []

    if row:
        kurs_keyboard.append(row)

    kurs_keyboard.append([Button.inline(text="🔙Назад", data="back4")])
    return kurs_keyboard
