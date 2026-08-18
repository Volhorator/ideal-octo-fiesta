#!/usr/bin/env python3
"""
attach_folder.py - скрипт привязки папки к заказу

Вызывается из Double Commander с параметром командной строки - путём к папке.
Предоставляет пользователю выбор заказа без привязанной папки или ручной ввод номера.
"""

import sys
import os

# Добавляем директорию скрипта в путь для импорта модулей
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from data_store import get_orders_without_folder, update_order, find_order_by_number


def main():
    # Получаем путь к папке из аргументов командной строки
    if len(sys.argv) < 2:
        print("Ошибка: не указан путь к папке.")
        print("Использование: python attach_folder.py <path_to_folder>")
        input("Нажмите Enter для выхода...")
        return 1
    
    folder_path = sys.argv[1]
    
    # Нормализуем путь (конвертируем обратные слеши в прямые для единообразия)
    folder_path = folder_path.replace('\\', '/')
    
    # Загружаем заказы без привязки папки
    orders_without_folder = get_orders_without_folder()
    
    if not orders_without_folder:
        print("Все заказы уже имеют привязку к папке.")
        print(f"Путь папки: {folder_path}")
        input("Нажмите Enter для выхода...")
        return 0
    
    print("=" * 60)
    print("Привязка папки к заказу")
    print(f"Папка: {folder_path}")
    print("=" * 60)
    print()
    
    # Выводим список заказов без папки
    print("Заказы без привязки папки:")
    print("-" * 60)
    
    for i, order in enumerate(orders_without_folder, 1):
        order_num = order.get("order_number", "Без номера")
        name = order.get("name", "")
        customer = order.get("customer", "")
        due_date = order.get("due_date", "")
        
        print(f"{i}. Номер: {order_num}")
        print(f"   Название: {name}")
        print(f"   Заказчик: {customer}")
        print(f"   Срок: {due_date}")
        print()
    
    print("-" * 60)
    print("Введите номер строки для выбора заказа ИЛИ введите номер заказа вручную.")
    print("Для отмены введите 'q' или 'exit'.")
    print()
    
    user_input = input("Ваш выбор: ").strip()
    
    if user_input.lower() in ('q', 'exit', 'отмена'):
        print("Отменено пользователем.")
        return 0
    
    selected_order = None
    
    # Пытаемся интерпретировать ввод как номер строки
    try:
        line_num = int(user_input)
        if 1 <= line_num <= len(orders_without_folder):
            selected_order = orders_without_folder[line_num - 1]
        else:
            print(f"Неверный номер строки. Доступно вариантов: 1-{len(orders_without_folder)}")
    except ValueError:
        # Если не число, считаем что это номер заказа
        selected_order = find_order_by_number(user_input)
        if selected_order is None:
            print(f"Заказ с номером '{user_input}' не найден.")
            input("Нажмите Enter для выхода...")
            return 1
    
    if selected_order is None:
        print("Заказ не выбран.")
        input("Нажмите Enter для выхода...")
        return 1
    
    # Привязываем папку к заказу
    order_number = selected_order.get("order_number")
    success = update_order(order_number, {"folder_path": folder_path})
    
    if success:
        print()
        print("=" * 60)
        print(f"Успешно! Папка привязана к заказу №{order_number}")
        print(f"Путь: {folder_path}")
        print("=" * 60)
    else:
        print()
        print("Ошибка при сохранении данных.")
        return 1
    
    input("Нажмите Enter для выхода...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
