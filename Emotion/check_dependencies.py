import subprocess
import sys

required_packages = [
    "aiogram==3.4.1",
    "aiohttp",
    "pydantic",
    "aiofiles",
    "certifi",
    "magic-filter"
]

def check_installed_packages():
    print("🔍 Перевірка встановлених пакетів у середовищі...")

    try:
        output = subprocess.check_output([sys.executable, "-m", "pip", "freeze"])
        installed = output.decode().splitlines()
        installed_names = [pkg.split("==")[0].lower() for pkg in installed]

        for pkg in required_packages:
            name = pkg.split("==")[0].lower()
            if not any(inst.lower().startswith(name) for inst in installed):
                print(f"⚠️ НЕ встановлено: {pkg}")
            else:
                print(f"✅ Встановлено: {pkg}")
    except Exception as e:
        print(f"❌ Помилка при перевірці пакетів: {e}")

if __name__ == "__main__":
    check_installed_packages()