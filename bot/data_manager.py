import json
import os
import time
from config import Config

class DataManager:
    @staticmethod
    def get_department(department_name):
        """Получение данных кафедры с правильным путем к файлу"""
        try:
            # Формируем правильное имя файла
            filename = f"{department_name}.json"
            filepath = os.path.join(Config.DEPARTMENTS_DIR, filename)
            
            # Проверяем существование файла
            if not os.path.exists(filepath):
                print(f"Файл не найден: {filepath}")
                return {"text": "Информация отсутствует", "photo": None}
            
            # Читаем файл
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
                # Проверяем структуру данных
                if not all(key in data for key in ['text', 'photo']):
                    print(f"Неверная структура в файле {filename}")
                    return {"text": "Информация отсутствует", "photo": None}
                    
                return data
                
        except json.JSONDecodeError:
            print(f"Ошибка чтения JSON из {filename}")
            return {"text": "Информация отсутствует", "photo": None}
        except Exception as e:
            print(f"Ошибка при чтении {filename}: {str(e)}")
            return {"text": "Информация отсутствует", "photo": None}

    @staticmethod
    def get_events():
        """Получить список мероприятий"""
        try:
            with open(Config.EVENTS_FILE, 'r', encoding='utf-8') as file:
                return json.load(file).get("events", [])
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    @staticmethod
    def save_photo(file_id, bot):
        """Сохранить фото и вернуть имя файла"""
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        filename = f"photo_{int(time.time())}.jpg"
        save_path = os.path.join(Config.IMAGES_DIR, filename)
        
        with open(save_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        
        return filename

    @staticmethod
    def update_department(department_name, text, photo):
        """Обновление данных кафедры с проверками"""
        try:
            # Нормализация имени файла
            filename = f"{department_name.lower().replace(' ', '_')}.json"
            filepath = os.path.join(Config.DEPARTMENTS_DIR, filename)
            
            # Проверка существования директории
            os.makedirs(Config.DEPARTMENTS_DIR, exist_ok=True)
            
            data = {
                "text": text,
                "photo": photo
            }
            
            # Запись с проверкой
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            print(f"DEBUG: Данные сохранены в {filepath}")  # Логирование
            return True
            
        except Exception as e:
            print(f"ERROR: Ошибка сохранения {department_name}: {str(e)}")
            return False

    @staticmethod
    def add_event(text, photo):
        """Добавить мероприятие"""
        events = DataManager.get_events()
        new_id = max([e.get("id", 0) for e in events], default=0) + 1
        events.append({"id": new_id, "text": text, "photo": photo})
        
        with open(Config.EVENTS_FILE, 'w', encoding='utf-8') as file:
            json.dump({"events": events}, file, ensure_ascii=False, indent=2)

    @staticmethod
    def delete_event(event_id):
        """Удалить мероприятие"""
        events = [e for e in DataManager.get_events() if e.get("id") != event_id]
        with open(Config.EVENTS_FILE, 'w', encoding='utf-8') as file:
            json.dump({"events": events}, file, ensure_ascii=False, indent=2)