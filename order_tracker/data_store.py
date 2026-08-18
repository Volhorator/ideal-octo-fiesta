"""
data_store.py - модуль работы с данными (CRUD операции для заказов)
"""

import json
import os
import tempfile
import shutil
from typing import Optional

from config import get_config


def _get_orders_path() -> str:
    """Возвращает полный путь к файлу заказов."""
    config = get_config()
    path = config.get("orders_file_path", "./orders.json")
    # Если путь относительный, делаем его относительно директории скрипта
    if not os.path.isabs(path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(script_dir, path)
    return path


def _load_lock_file_path() -> str:
    """Возвращает путь к файлу блокировки."""
    orders_path = _get_orders_path()
    return orders_path + ".lock"


def load_orders() -> list:
    """
    Загружает список заказов из JSON-файла.
    
    :return: список словарей с заказами
    """
    orders_path = _get_orders_path()
    
    if not os.path.exists(orders_path):
        return []
    
    with open(orders_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not isinstance(data, list):
        return []
    
    return data


def save_orders(orders: list) -> bool:
    """
    Сохраняет список заказов в JSON-файл (атомарная запись через временный файл).
    
    :param orders: список словарей с заказами
    :return: True если сохранение успешно
    """
    orders_path = _get_orders_path()
    lock_path = _load_lock_file_path()
    
    # Простая блокировка через создание lock-файла
    if os.path.exists(lock_path):
        # В реальном приложении можно добавить ожидание или повторные попытки
        pass
    
    try:
        # Создаём lock-файл
        with open(lock_path, 'w') as f:
            f.write(str(os.getpid()))
        
        # Запись во временный файл с последующим переименованием
        dir_name = os.path.dirname(orders_path)
        fd, temp_path = tempfile.mkstemp(suffix='.json', dir=dir_name)
        
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(orders, f, ensure_ascii=False, indent=2)
            
            # Атомарное переименование
            shutil.move(temp_path, orders_path)
        except Exception:
            # При ошибке удаляем временный файл
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise
    finally:
        # Удаляем lock-файл
        if os.path.exists(lock_path):
            os.remove(lock_path)
    
    return True


def add_order(order: dict) -> bool:
    """
    Добавляет новый заказ в хранилище.
    
    :param order: словарь с данными заказа (должен содержать order_number)
    :return: True если добавление успешно
    """
    orders = load_orders()
    
    # Проверяем уникальность номера заказа
    for existing in orders:
        if existing.get("order_number") == order.get("order_number"):
            return False  # Заказ с таким номером уже существует
    
    orders.append(order)
    return save_orders(orders)


def update_order(order_number: str, updated_fields: dict) -> bool:
    """
    Обновляет поля существующего заказа.
    
    :param order_number: номер заказа для обновления
    :param updated_fields: словарь с полями для обновления
    :return: True если обновление успешно
    """
    orders = load_orders()
    
    for i, order in enumerate(orders):
        if order.get("order_number") == order_number:
            orders[i].update(updated_fields)
            return save_orders(orders)
    
    return False  # Заказ не найден


def delete_order(order_number: str) -> bool:
    """
    Удаляет заказ по номеру.
    
    :param order_number: номер заказа для удаления
    :return: True если удаление успешно
    """
    orders = load_orders()
    
    initial_len = len(orders)
    orders = [o for o in orders if o.get("order_number") != order_number]
    
    if len(orders) < initial_len:
        return save_orders(orders)
    
    return False  # Заказ не найден


def find_order_by_number(number: str) -> Optional[dict]:
    """
    Ищет заказ по номеру.
    
    :param number: номер заказа для поиска
    :return: словарь с данными заказа или None если не найден
    """
    orders = load_orders()
    
    for order in orders:
        if order.get("order_number") == number:
            return order
    
    return None


def get_orders_without_folder() -> list:
    """
    Возвращает список заказов, у которых не указана папка (folder_path пуст или отсутствует).
    
    :return: список словарей с заказами без привязки папки
    """
    orders = load_orders()
    
    result = []
    for order in orders:
        folder_path = order.get("folder_path", "")
        if not folder_path or folder_path.strip() == "":
            result.append(order)
    
    return result


def get_all_orders() -> list:
    """
    Возвращает все заказы (алиас для load_orders).
    
    :return: список всех заказов
    """
    return load_orders()
