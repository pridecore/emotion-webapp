import json
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def load_psychologists():
    
    with open("data/approved_psychologists.json", "r", encoding="utf-8") as file:
        return json.load(file)

def get_psychologists_by_spec(spec):
    psychologists = load_psychologists()
    matched = []
    for p in psychologists:
        spec_list = [s.strip() for s in p.get("specializations", "").split(",")]
        if spec in spec_list:
            matched.append(p)
    return matched

def get_psychologists_keyboard(psychologists):
    buttons = []
    for p in psychologists:
        button_text = f"{p['fullname']} — {p.get('price', 'Ціну уточнюйте')} грн"
        buttons.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"psy_{p['login']}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)