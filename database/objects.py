import os
from dotenv import load_dotenv
from coder import Coder

# Путь к .env файлу (по умолчанию в корневой директории проекта)
ENV_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")

def load_or_create_secret_key():
    # Загружаем переменные из .env файла
    load_dotenv(ENV_FILE)
    
    # Проверяем, существует ли secret_key
    if "secret_key" in os.environ:
        return os.environ["secret_key"]
    
    # Создаем новый ключ, если его нет
    secret_key = Coder.get_secret_key()
    
    # Записываем ключ в .env файл
    append_mode = 'a' if os.path.exists(ENV_FILE) else 'w'
    with open(ENV_FILE, append_mode) as f:
        f.write(f"\nsecret_key={secret_key}")
    
    os.environ["secret_key"] = secret_key
    return secret_key

# Загружаем или создаем ключ
secret_key = load_or_create_secret_key()
coder = Coder(secret_key)
