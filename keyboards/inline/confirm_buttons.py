from telethon.tl.custom import Button

# Kursni o'chirishni tasdiqlash tugmalari
def confirm_delete_buttons(kurs_id: int):
    return [
        [Button.inline("Ha", data=f"confirm_yes_{kurs_id}")],
        [Button.inline("Yo'q", data=f"confirm_no_{kurs_id}")]
    ]
