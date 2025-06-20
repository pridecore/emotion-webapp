from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- МАПА СПЕЦІАЛІЗАЦІЙ З КАТЕГОРІЯМИ ---
CATEGORY_MAP = {
    "🧍‍♀️ Про себе": [
        "Втрата", "Суїцидальні думки", "Самооцінка", "Тривожність", "Панічні атаки",
        "Фобії", "Страхи", "Апатія", "Залежності", "РХП", "ПТСР", "Стрес",
        "Психосоматика", "Негативні думки"
    ],
    "🫂 Про стосунки": [
        "Сексуальність", "Відносини", "Сімейні відносини", "Особисті кордони", "Насильство"
    ],
    "🎯 Про діяльність": [
        "Відсутність мотивації", "Прокрастинація"
    ],
    "🌍 Про адаптацію": [
        "Вигорання", "Адаптація", "Психотравма", "Невизначеність", "Кризові стани", "Депресивний стан"
    ],
    "🪖 Про війну": [
        "Зниклі безвісті", "Війна"
    ]
}

# Створюємо короткий унікальний ключ для кожної спеціалізації
short_spec_map = {}
spec_index = 0
for category, specs in CATEGORY_MAP.items():
    for spec in specs:
        key = f"s{spec_index}"
        short_spec_map[key] = spec
        spec_index += 1

# --- КЛАВІАТУРА ВСІХ ЗАПИТІВ ---
def get_all_specializations_keyboard(selected=None):
    if selected is None:
        selected = []

    builder = InlineKeyboardBuilder()

    for category_label, specs in CATEGORY_MAP.items():
        builder.row(
            InlineKeyboardButton(text=f"— {category_label} —", callback_data="noop")
        )
        for spec in specs:
            key = [k for k, v in short_spec_map.items() if v == spec][0]
            is_selected = spec in selected
            text = f"✅ {spec}" if is_selected else spec
            builder.row(
                InlineKeyboardButton(
                    text=text,
                    callback_data=f"t:{key}"
                )
            )

    builder.row(
        InlineKeyboardButton(text="🔎 Пошук", callback_data="show_all"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_categories")
    )

    return builder.as_markup()

# Доступ до повної назви за ключем
def get_spec_by_key(short_key: str) -> str:
    return short_spec_map.get(short_key, "")