from telethon.tl.custom import Button

def course(listt, row_width=2):
    kurs_keyboard = []
    row = []

    for kurs1 in listt:
        row.append(Button.inline(text=kurs1[1], data=f"courses_{kurs1[0]}"))

        if len(row) == row_width:
            kurs_keyboard.append(row)
            row = []

    if row:
        kurs_keyboard.append(row)

    # kurs_keyboard.append([Button.inline(text="🔙Ortga", data="backk")])
    return kurs_keyboard


def user_ALL(listt, row_width=2):
    kurs_keyboard = []
    row = []

    for kurs1 in listt:
        row.append(Button.inline(text=kurs1[1], data=f"USER_{kurs1[0]}"))

        if len(row) == row_width:
            kurs_keyboard.append(row)
            row = []

    if row:
        kurs_keyboard.append(row)

    # kurs_keyboard.append([Button.inline(text="🔙Ortga", data="backk")])
    return kurs_keyboard
