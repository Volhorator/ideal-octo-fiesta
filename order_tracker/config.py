"""
config.py - модуль загрузки конфигурации приложения
"""

import json
import os

DEFAULT_CONFIG = {
    "double_commander_command": "doublecmd",
    "search_url": "http://intranet.example.com/search",
    "search_post_data_template": '{"fio": "{query}"}',
    "orders_file_path": "./orders.json"
}


def load_config(config_path: str = None) -> dict:
    """
    Загружает конфигурацию из JSON-файла.
    Если файл не найден, возвращает значения по умолчанию.
    
    :param config_path: путь к файлу конфигурации (по умолчанию ./config.json)
    :return: словарь с конфигурацией
    """
    if config_path is None:
        # Ищем config.json в той же директории, где лежит скрипт
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, "config.json")
    
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        # Объединяем с дефолтными значениями на случай отсутствия ключей
        result = DEFAULT_CONFIG.copy()
        result.update(config)
        return result
    else:
        return DEFAULT_CONFIG.copy()


# Глобальный экземпляр конфигурации (ленивая загрузка)
_config = None


def get_config() -> dict:
    """
    Возвращает конфигурацию приложения (загружается один раз при первом вызове).
    
    :return: словарь с конфигурацией
    """
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reload_config():
    """
    Принудительно перезагружает конфигурацию из файла.
    """
    global _config
    _config = load_config()
