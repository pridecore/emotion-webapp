import hashlib
import urllib.parse

def generate_jitsi_link(psychologist_login: str, datetime_str: str) -> str:
    # Хешуємо унікальний ідентифікатор зустрічі
    raw_string = f"{psychologist_login}-{datetime_str}"
    unique_hash = hashlib.sha256(raw_string.encode()).hexdigest()[:10]

    # Кодуємо назву кімнати
    room_name = f"EmotionMeet_{psychologist_login}_{unique_hash}"
    encoded_room = urllib.parse.quote(room_name)

    # Повне посилання на Jitsi
    return f"https://meet.jit.si/{encoded_room}"