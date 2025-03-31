import telebot
from telebot import types
from config import Config
from data_manager import DataManager
from keyboard_manager import KeyboardManager
from admin_manager import AdminManager
import os

# Инициализация бота
bot = telebot.TeleBot(Config.BOT_TOKEN)
admin_manager = AdminManager(bot)

# ==================== Обработчики команд ====================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        Config.WELCOME_MESSAGE,
        reply_markup=KeyboardManager.template_menu()
    )
    bot.send_message(
        message.chat.id,
        "Выберите раздел:",
        reply_markup=KeyboardManager.main_menu()
    )

@bot.message_handler(commands=['info'])
def send_info(message):
    bot.send_message(
        message.chat.id,
        Config.INFO_MESSAGE,
        reply_markup=KeyboardManager.template_menu()
    )

@bot.message_handler(commands=['admin'])
def handle_admin(message):
    admin_manager.handle_command(message)

# ==================== Обработчики сообщений ====================
@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == "🔍 К разделам":
        bot.send_message(
            message.chat.id,
            "Выберите раздел:",
            reply_markup=KeyboardManager.main_menu()
        )
    elif message.text == "ℹ️ Информация":
        send_info(message)
    else:
        admin_manager.handle_message(message)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    admin_manager.handle_photo(message)

# ==================== Обработчики callback ====================
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        if call.data == 'departments':
            show_departments_menu(call.message)
        elif call.data == 'events':
            show_events(call.message)
        elif call.data.startswith('department_'):
            show_department(call)
        elif call.data == 'back_to_main':
            show_main_menu(call.message)
        elif call.data.startswith('admin_'):
            admin_manager.handle_callback(call)
    except Exception as e:
        error_msg = f"⚠️ Ошибка: {str(e)}"
        bot.send_message(call.message.chat.id, error_msg)

# ==================== Вспомогательные функции ====================
def show_departments_menu(message):
    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text="Выберите кафедру:",
        reply_markup=KeyboardManager.departments_menu()
    )

def show_events(message):
    events = DataManager.get_events()
    if not events:
        bot.answer_callback_query(message.id, "Нет доступных мероприятий")
        return
    
    bot.send_message(
        message.chat.id,
        "📅 Ближайшие мероприятия:",
        reply_markup=KeyboardManager.template_menu()
    )
    
    for event in events:
        try:
            with open(os.path.join(Config.IMAGES_DIR, event['photo']), 'rb') as photo:
                bot.send_photo(
                    message.chat.id,
                    photo,
                    caption=event['text']
                )
        except Exception as e:
            bot.send_message(message.chat.id, event['text'])

def show_department(call):
    department_name = call.data.split('_')[1]
    print(f"Запрошена кафедра: {department_name}")  # Логирование
    
    department = DataManager.get_department(department_name)
    print(f"Полученные данные: {department}")  # Логирование
    
    if not department or 'text' not in department:
        bot.send_message(
            call.message.chat.id,
            "Информация отсутствует",
            reply_markup=KeyboardManager.template_menu()
        )
        return
    
    try:
        # Проверяем наличие фото
        if department.get('photo'):
            photo_path = os.path.join(Config.IMAGES_DIR, department['photo'])
            if os.path.exists(photo_path):
                with open(photo_path, 'rb') as photo:
                    bot.send_photo(
                        call.message.chat.id,
                        photo,
                        caption=department['text'],
                        reply_markup=KeyboardManager.template_menu()
                    )
            else:
                bot.send_message(
                    call.message.chat.id,
                    department['text'],
                    reply_markup=KeyboardManager.template_menu()
                )
        else:
            bot.send_message(
                call.message.chat.id,
                department['text'],
                reply_markup=KeyboardManager.template_menu()
            )
    except Exception as e:
        print(f"Ошибка при выводе: {str(e)}")
        bot.send_message(
            call.message.chat.id,
            "Ошибка при отображении информации",
            reply_markup=KeyboardManager.template_menu()
        )

def show_main_menu(message):
    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text="Выберите раздел:",
        reply_markup=KeyboardManager.main_menu()
    )

if __name__ == '__main__':
    print("🤖 Бот запущен...")
    bot.polling(none_stop=True)