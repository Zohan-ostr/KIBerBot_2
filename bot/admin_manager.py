from telebot import types
from data_manager import DataManager
from keyboard_manager import KeyboardManager
from config import Config
import os

class AdminManager:
    def __init__(self, bot):
        self.bot = bot
        self.user_states = {}

    def check_admin(self, user_id):
        """Проверить права администратора"""
        return user_id in Config.ADMIN_IDS

    def handle_command(self, message):
        """Обработка команды /admin"""
        if self.check_admin(message.chat.id):
            self.bot.send_message(
                message.chat.id,
                "🔐 Админ-панель:",
                reply_markup=KeyboardManager.admin_menu()
            )
        else:
            self.bot.send_message(message.chat.id, "⛔ У вас нет доступа!")

    def handle_callback(self, call):
        if not self.check_admin(call.message.chat.id):
            self.bot.answer_callback_query(call.id, "⛔ Доступ запрещен")
            return

        try:
            if call.data == 'admin_add':
                self._show_add_menu(call)
            elif call.data == 'admin_add_dept':
                self._show_department_selection(call)
            elif call.data.startswith('admin_add_dept_'):
                self._start_adding_department(call)
            elif call.data == 'admin_add_event':
                self._start_adding_event(call)
        except Exception as e:
            self.bot.send_message(call.message.chat.id, f"⚠️ Ошибка: {str(e)}")
            print(f"Error in callback: {str(e)}")

    def handle_message(self, message):
        """Обработка текстовых сообщений админа"""
        user_id = message.chat.id
        if user_id not in self.user_states:
            return

        state = self.user_states[user_id].get("state")
        
        if state == "adding_department_text":
            self._process_department_text(message)
        elif state == "adding_event_text":
            self._process_event_text(message)

    def handle_photo(self, message):
        """Обработка фото от админа"""
        user_id = message.chat.id
        if user_id not in self.user_states:
            return

        state = self.user_states[user_id].get("state")
        
        if state == "adding_department_photo":
            self._process_department_photo(message)
        elif state == "adding_event_photo":
            self._process_event_photo(message)

    # Приватные методы для обработки состояний
    def _show_add_menu(self, call):
        markup = types.InlineKeyboardMarkup(row_width=2)
        dept_btn = types.InlineKeyboardButton("Кафедру", callback_data='admin_add_dept')
        event_btn = types.InlineKeyboardButton("Мероприятие", callback_data='admin_add_event')
        markup.add(dept_btn, event_btn)
        
        self.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Что вы хотите добавить?",
            reply_markup=markup
        )

    def _show_department_selection(self, call):
        """Показывает меню выбора кафедры"""
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = [
            types.InlineKeyboardButton(
                name,
                callback_data=f"admin_add_dept_{key}"
            ) for key, name in Config.DEPARTMENTS.items()
        ]
        markup.add(*buttons)
        markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data='admin_back'))
        
        self.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Выберите кафедру для редактирования:",
            reply_markup=markup
        )

    def _start_adding_department(self, call):
        """Обработка выбора конкретной кафедры"""
        department_key = call.data.split('admin_add_dept_')[-1]
        
        # Проверяем что кафедра существует
        if department_key not in Config.DEPARTMENTS:
            self.bot.answer_callback_query(call.id, "❌ Кафедра не найдена")
            return
        
        # Сохраняем состояние
        self.user_states[call.message.chat.id] = {
            "state": "adding_department_text",
            "department": department_key,
            "message_id": call.message.message_id  # Сохраняем ID сообщения
        }
        
        # Запрашиваем текст
        self.bot.send_message(
            call.message.chat.id,
            f"✏️ Введите текст для кафедры {Config.DEPARTMENTS[department_key]}:",
            reply_markup=types.ReplyKeyboardRemove()
        )

    def _process_department_text(self, message):
        """Обработка текста кафедры"""
        if message.chat.id not in self.user_states:
            return
            
        department_key = self.user_states[message.chat.id]["department"]
        
        # Обновляем состояние
        self.user_states[message.chat.id].update({
            "text": message.text,
            "state": "adding_department_photo"
        })
        
        # Запрашиваем фото
        self.bot.send_message(
            message.chat.id,
            f"📷 Теперь отправьте фото для кафедры {Config.DEPARTMENTS[department_key]}:",
            reply_markup=types.ReplyKeyboardRemove()
        )

    def _process_department_photo(self, message):
        department = self.user_states[message.chat.id]["department"]
        text = self.user_states[message.chat.id]["text"]
        photo = DataManager.save_photo(message.photo[-1].file_id, self.bot)
        
        DataManager.update_department(department, text, photo)
        self.bot.send_message(
            message.chat.id,
            f"✅ Кафедра {Config.DEPARTMENTS[department]} обновлена!",
            reply_markup=KeyboardManager.template_menu()
        )
        del self.user_states[message.chat.id]

    def _start_adding_event(self, call):
        """Начало добавления мероприятия"""
        self.user_states[call.message.chat.id] = {
            "state": "adding_event_text"
        }
        self.bot.send_message(
            call.message.chat.id,
            "Введите текст мероприятия:",
            reply_markup=types.ReplyKeyboardRemove()
        )

    def _process_event_text(self, message):
        """Обработка текста мероприятия"""
        self.user_states[message.chat.id].update({
            "text": message.text,
            "state": "adding_event_photo"
        })
        self.bot.send_message(
            message.chat.id,
            "Теперь отправьте фото для мероприятия:",
            reply_markup=types.ReplyKeyboardRemove()
        )

    def _process_event_photo(self, message):
        """Обработка фото мероприятия"""
        text = self.user_states[message.chat.id]["text"]
        photo = DataManager.save_photo(message.photo[-1].file_id, self.bot)
        
        DataManager.add_event(text, photo)
        self.bot.send_message(
            message.chat.id,
            "✅ Мероприятие успешно добавлено!",
            reply_markup=KeyboardManager.template_menu()
        )
        del self.user_states[message.chat.id]