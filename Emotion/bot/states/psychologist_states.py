from aiogram.fsm.state import StatesGroup, State

class PsychologistLogin(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()

class PsychologistRegister(StatesGroup):
    waiting_for_photo = State()
    fullname = State()
    specializations = State()
    experience_desc = State()
    education = State()
    years_exp = State()
    price = State()
    languages = State()
    login = State()
    password = State()
    
    # 🔄 Графік
    picking_days = State()
    picking_start_time = State()
    picking_end_time = State()



class Booking(StatesGroup):
    choosing_date = State()
    choosing_time = State()
    confirming = State()

    awaiting_payment = State()