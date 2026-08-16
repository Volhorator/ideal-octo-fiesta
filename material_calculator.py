#!/usr/bin/env python3
"""
Программа для подсчёта необходимого количества материала.
Решает задачу раскроя (cutting stock problem) жадным алгоритмом.
"""

import sys
from typing import List, Tuple


def read_from_console() -> Tuple[float, List[Tuple[float, int]]]:
    """Чтение данных из консоли."""
    print("Введите длину материала (например, 6 для 6 метров):")
    stock_length = float(input().strip())
    
    print("Введите количество различных размеров деталей:")
    num_types = int(input().strip())
    
    parts = []
    print(f"Введите {num_types} строк в формате: <длина> <количество>")
    for _ in range(num_types):
        line = input().strip()
        length, count = map(float, line.split())
        parts.append((length, int(count)))
    
    return stock_length, parts


def read_from_file(filename: str) -> Tuple[float, List[Tuple[float, int]]]:
    """Чтение данных из файла.
    
    Формат файла:
    Первая строка: длина материала
    Далее строки: <длина детали> <количество>
    
    Пример:
    6
    3 4
    2 6
    1 12
    """
    with open(filename, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    stock_length = float(lines[0])
    parts = []
    
    for line in lines[1:]:
        length, count = map(float, line.split())
        parts.append((length, int(count)))
    
    return stock_length, parts


def calculate_material(stock_length: float, parts: List[Tuple[float, int]]) -> int:
    """
    Подсчёт необходимого количества материала usando жадный алгоритм.
    
    Args:
        stock_length: Длина одной единицы материала
        parts: Список кортежей (длина детали, количество)
    
    Returns:
        Необходимое количество единиц материала
    """
    # Создаём список всех деталей
    all_parts = []
    for length, count in parts:
        if length > stock_length:
            print(f"Предупреждение: деталь длиной {length} больше длины материала {stock_length}")
        all_parts.extend([length] * count)
    
    # Сортируем детали по убыванию (для лучшего результата жадного алгоритма)
    all_parts.sort(reverse=True)
    
    stocks_used = []  # Список использованных материалов с остатком
    
    for part_length in all_parts:
        placed = False
        
        # Пытаемся разместить деталь в существующем материале
        for i, remaining in enumerate(stocks_used):
            if remaining >= part_length:
                stocks_used[i] -= part_length
                placed = True
                break
        
        # Если не удалось, берём новый материал
        if not placed:
            stocks_used.append(stock_length - part_length)
    
    return len(stocks_used)


def main():
    print("=== Калькулятор необходимого количества материала ===\n")
    
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        print(f"Чтение данных из файла: {filename}")
        try:
            stock_length, parts = read_from_file(filename)
        except FileNotFoundError:
            print(f"Ошибка: файл '{filename}' не найден")
            sys.exit(1)
        except Exception as e:
            print(f"Ошибка при чтении файла: {e}")
            sys.exit(1)
    else:
        print("Чтение данных из консоли\n")
        stock_length, parts = read_from_console()
    
    print(f"\nДлина материала: {stock_length} м")
    print("Список деталей:")
    for length, count in parts:
        print(f"  {length} м - {count} шт.")
    
    result = calculate_material(stock_length, parts)
    
    print(f"\nРезультат: {result} (штук {stock_length}-метровых досок)")


if __name__ == "__main__":
    main()
