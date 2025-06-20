from aiogram.fsm.state import State, StatesGroup


class ClientForm(StatesGroup):

    # Крок 1 — короткий опис проблеми
    writing_problem = State()

    # Крок 2 — як давно триває проблема
    writing_duration = State()

    # Крок 3 — очікування від консультації
    writing_expectations = State()

    # Крок 4 — зручний час (загальні побажання)
    writing_preferred_time = State()

    current_state = State()
    gender_preference = State()
    frequency = State()
    communication_style = State()
    age = State()
    final_confirmation = State()


class Booking(StatesGroup):

    # Крок 1 — вибір дати
    choosing_date = State()

    # Крок 2 — вибір часу
    choosing_time = State()

    # Крок 3 — підтвердження бронювання (поки не використовується)
    confirming = State()

    awaiting_payment = State()

    selecting_day = State()
    selecting_start_time = State()
    selecting_end_time = State()

class FeedbackForm(StatesGroup):
    waiting_feedback = State()


class ReminderForm(StatesGroup):
    waiting_for_time = State()
