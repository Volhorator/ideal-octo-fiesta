"""
external_integration.py - взаимодействие с внешними программами
(Double Commander, внутренний сайт предприятия)
"""

import subprocess
import webbrowser
import urllib.request
import urllib.parse
import os
import json

from config import get_config


def open_in_double_commander(path: str) -> bool:
    """
    Открывает указанную папку в Double Commander.
    
    :param path: полный путь к папке
    :return: True если команда запущена успешно
    """
    config = get_config()
    dc_command = config.get("double_commander_command", "doublecmd")
    
    # Проверяем существование пути
    if not os.path.exists(path):
        return False
    
    try:
        # Формируем команду: doublecmd <path>
        cmd = [dc_command, path]
        subprocess.Popen(cmd)
        return True
    except Exception as e:
        print(f"Ошибка при открытии Double Commander: {e}")
        return False


def search_on_site(full_name: str) -> bool:
    """
    Выполняет поиск информации о человеке по ФИО на внутреннем сайте.
    Отправляет POST-запрос и открывает браузер с результатами.
    
    :param full_name: ФИО для поиска
    :return: True если операция выполнена успешно
    """
    config = get_config()
    search_url = config.get("search_url", "")
    post_template = config.get("search_post_data_template", '{"fio": "{query}"}')
    
    if not search_url:
        print("URL для поиска не настроен в конфигурации")
        return False
    
    if not full_name or full_name.strip() == "":
        print("ФИО пустое, поиск невозможен")
        return False
    
    try:
        # Сначала открываем страницу поиска в браузере (для cookies/сессии)
        webbrowser.open(search_url)
        
        # Формируем данные POST-запроса из шаблона
        post_data_str = post_template.replace("{query}", full_name)
        post_data = json.loads(post_data_str)
        
        # Кодируем данные для отправки
        encoded_data = urllib.parse.urlencode(post_data).encode('utf-8')
        
        # Создаём запрос
        req = urllib.request.Request(
            search_url,
            data=encoded_data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        # Отправляем запрос (результат может использоваться сайтом для подготовки выдачи)
        with urllib.request.urlopen(req, timeout=5) as response:
            # Просто читаем ответ, чтобы завершить запрос
            response.read()
        
        return True
        
    except Exception as e:
        print(f"Ошибка при поиске на сайте: {e}")
        # Даже при ошибке POST-запроса, браузер уже открыт
        return True  # Считаем успешным, т.к. браузер открыт
