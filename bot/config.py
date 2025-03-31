import os
from dotenv import load_dotenv
import hashlib

load_dotenv()

class Config:
    # Основные настройки
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
    
    if not all([BOT_TOKEN, ADMIN_PASSWORD]):
        raise ValueError("Необходимо установить BOT_TOKEN и ADMIN_PASSWORD в .env файле!")
    
    ADMIN_PASSWORD_HASH = hashlib.sha256(ADMIN_PASSWORD.encode()).hexdigest()
    ADMIN_IDS = [int(id) for id in os.getenv('ADMIN_IDS', '').split(',') if id]
    
    # Пути к файлам
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    DEPARTMENTS_DIR = os.path.join(DATA_DIR, 'departments')
    EVENTS_FILE = os.path.join(DATA_DIR, 'events.json')
    IMAGES_DIR = os.path.join(BASE_DIR, 'images')
    
    # Создаем необходимые директории
    os.makedirs(DEPARTMENTS_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)
    
    # Названия кафедр с emoji
    DEPARTMENTS = {
        'IndustrialInformatics': "🏭 Промышленная информатика",
        'Biocybernetics': "🧬 Биокибернетика",
        'SystemsEngineering': "⚙️ Системная инженерия",
        'AiTechnologies': "🤖 ИИ технологии",
        'HigherMathematics': "🧮 Высшая математика",
        'ManagementProblems': "📊 Проблемы управления",
        'AutomaticSystems': "🤖 Автоматические системы",
        'ComputerSecurity': "🔒 Компьютерная безопасность"
    }
    
    # Текстовые сообщения
    WELCOME_MESSAGE = """
👋 Добро пожаловать в информационный бот кафедр!

Здесь вы можете узнать о:
• Направлениях подготовки
• Преподавателях
• Ближайших мероприятиях
"""
    INFO_MESSAGE = """
ℹ️ Справка по боту:

🔹 "К разделам" - главное меню
🔹 "Информация" - это сообщение
🔹 Для админов - команда /admin

По вопросам: @username
"""