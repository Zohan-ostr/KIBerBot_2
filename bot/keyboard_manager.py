from telebot import types
from config import Config

class KeyboardManager:
    @staticmethod
    def main_menu():
        """Главное меню с inline-кнопками"""
        markup = types.InlineKeyboardMarkup(row_width=2)
        departments = types.InlineKeyboardButton("🏛 Кафедры", callback_data='departments')
        events = types.InlineKeyboardButton("📅 Мероприятия", callback_data='events')
        markup.add(departments, events)
        return markup

    @staticmethod
    def template_menu():
        """Reply-клавиатура с основными кнопками"""
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        sections = types.KeyboardButton("🔍 К разделам")
        info = types.KeyboardButton("ℹ️ Информация")
        markup.add(sections, info)
        return markup

    @staticmethod
    def departments_menu():
        """Меню выбора кафедры"""
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = [
            types.InlineKeyboardButton(name, callback_data=f"department_{key}")
            for key, name in Config.DEPARTMENTS.items()
        ]
        markup.add(*buttons)
        markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data='back_to_main'))
        return markup

    @staticmethod
    def admin_menu():
        """Меню администратора"""
        markup = types.InlineKeyboardMarkup(row_width=2)
        add_btn = types.InlineKeyboardButton("➕ Добавить", callback_data='admin_add')
        del_btn = types.InlineKeyboardButton("🗑️ Удалить", callback_data='admin_delete')
        edit_btn = types.InlineKeyboardButton("✏️ Редактировать", callback_data='admin_edit')
        markup.add(add_btn, del_btn, edit_btn)
        return markup