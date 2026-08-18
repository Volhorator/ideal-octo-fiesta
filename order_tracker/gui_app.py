#!/usr/bin/env python3
"""
gui_app.py - основное GUI-приложение для учёта заказов на Tkinter

Функционал:
- Отображение списка заказов в табличном виде (Treeview)
- Сортировка по любому столбцу
- Добавление, редактирование, удаление заказов
- Открытие папки в Double Commander
- Поиск заказчика/технолога на внутреннем сайте
- Фильтрация по номеру заказа
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import sys

# Добавляем директорию скрипта в путь для импорта модулей
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from data_store import (
    load_orders, save_orders, add_order, update_order, 
    delete_order, find_order_by_number, get_all_orders
)
from external_integration import open_in_double_commander, search_on_site


# Столбцы таблицы заказов
COLUMNS = [
    ("order_number", "Номер заказа", 100),
    ("order_type", "Тип", 120),
    ("drawing_number", "Чертеж", 120),
    ("name", "Название", 200),
    ("quantity", "Кол-во", 80),
    ("due_date", "Срок", 100),
    ("customer", "Заказчик", 150),
    ("technologist", "Технолог", 150),
    ("comment", "Комментарий", 200),
    ("folder_path", "Папка", 250),
]


class OrderDialog(simpledialog.Dialog):
    """Диалог добавления/редактирования заказа."""
    
    def __init__(self, parent, title, order_data=None):
        self.order_data = order_data or {}
        self.result_data = None
        super().__init__(parent, title)
    
    def body(self, master):
        """Создание полей диалога."""
        self.fields = {}
        
        row = 0
        for field_id, field_label, _ in COLUMNS:
            label = ttk.Label(master, text=field_label + ":")
            label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=3)
            
            entry = ttk.Entry(master, width=40)
            entry.grid(row=row, column=1, padx=5, pady=3)
            
            # Заполняем существующими данными
            value = self.order_data.get(field_id, "")
            if value is None:
                value = ""
            entry.insert(0, str(value))
            
            self.fields[field_id] = entry
            row += 1
        
        return master
    
    def apply(self):
        """Сбор данных из полей при нажатии OK."""
        self.result_data = {}
        for field_id, entry in self.fields.items():
            value = entry.get().strip()
            # Для quantity пытаемся преобразовать в число
            if field_id == "quantity":
                if value:
                    try:
                        value = int(value)
                    except ValueError:
                        value = 0
                else:
                    value = 0
            self.result_data[field_id] = value


class OrdersApp:
    """Основное приложение для управления заказами."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Учёт заказов")
        self.root.geometry("1200x600")
        
        self.orders = []
        self.sort_column = None
        self.sort_reverse = False
        
        self._create_widgets()
        self._load_data()
    
    def _create_widgets(self):
        """Создание виджетов интерфейса."""
        # Верхняя панель с кнопками и поиском
        top_frame = ttk.Frame(self.root, padding="5")
        top_frame.pack(side=tk.TOP, fill=tk.X)
        
        # Кнопки действий
        btn_add = ttk.Button(top_frame, text="Добавить заказ", command=self._add_order)
        btn_add.pack(side=tk.LEFT, padx=2)
        
        btn_edit = ttk.Button(top_frame, text="Редактировать", command=self._edit_order)
        btn_edit.pack(side=tk.LEFT, padx=2)
        
        btn_delete = ttk.Button(top_frame, text="Удалить", command=self._delete_order)
        btn_delete.pack(side=tk.LEFT, padx=2)
        
        btn_open_folder = ttk.Button(top_frame, text="Открыть папку", command=self._open_folder)
        btn_open_folder.pack(side=tk.LEFT, padx=2)
        
        btn_search_customer = ttk.Button(top_frame, text="Поиск заказчика", command=self._search_customer)
        btn_search_customer.pack(side=tk.LEFT, padx=2)
        
        btn_search_technologist = ttk.Button(top_frame, text="Поиск технолога", command=self._search_technologist)
        btn_search_technologist.pack(side=tk.LEFT, padx=2)
        
        # Поле поиска по номеру заказа
        search_frame = ttk.Frame(top_frame)
        search_frame.pack(side=tk.RIGHT)
        
        ttk.Label(search_frame, text="Поиск по номеру:").pack(side=tk.LEFT, padx=2)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._filter_orders)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=2)
        
        # Таблица заказов
        table_frame = ttk.Frame(self.root)
        table_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = [col[0] for col in COLUMNS]
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        # Настройка заголовков столбцов
        for col_id, col_name, width in COLUMNS:
            self.tree.heading(col_id, text=col_name, 
                             command=lambda c=col_id: self._sort_by_column(c))
            self.tree.column(col_id, width=width)
        
        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Привязка двойного клика для редактирования
        self.tree.bind('<Double-1>', lambda e: self._edit_order())
    
    def _load_data(self):
        """Загрузка данных из хранилища."""
        self.orders = load_orders()
        self._refresh_treeview()
    
    def _refresh_treeview(self):
        """Обновление отображения таблицы."""
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Применяем фильтрацию по поиску
        filtered_orders = self._apply_filter(self.orders)
        
        # Применяем сортировку
        if self.sort_column:
            reverse = self.sort_reverse
            key_func = self._get_sort_key(self.sort_column)
            filtered_orders = sorted(filtered_orders, key=key_func, reverse=reverse)
        
        # Заполняем таблицу
        for order in filtered_orders:
            values = tuple(str(order.get(col[0], "")) for col in COLUMNS)
            self.tree.insert('', tk.END, values=values)
    
    def _apply_filter(self, orders_list):
        """Применение фильтра по номеру заказа."""
        search_term = self.search_var.get().strip().lower()
        if not search_term:
            return orders_list
        
        return [
            order for order in orders_list
            if search_term in str(order.get("order_number", "")).lower()
        ]
    
    def _filter_orders(self, *args):
        """Обработчик изменения поля поиска."""
        self._refresh_treeview()
    
    def _get_sort_key(self, column):
        """Возвращает функцию ключа сортировки для столбца."""
        def key_func(order):
            value = order.get(column, "")
            if column == "quantity":
                try:
                    return int(value) if value else 0
                except (ValueError, TypeError):
                    return 0
            return str(value).lower() if value else ""
        return key_func
    
    def _sort_by_column(self, column):
        """Обработчик щелчка по заголовку столбца."""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        
        self._refresh_treeview()
    
    def _get_selected_order(self):
        """Возвращает данные выбранного заказа или None."""
        selection = self.tree.selection()
        if not selection:
            return None
        
        # Получаем значения из выбранной строки
        values = self.tree.item(selection[0])['values']
        
        # Ищем соответствующий заказ в списке
        order_number = values[0]  # Первый столбец - номер заказа
        return find_order_by_number(order_number)
    
    def _add_order(self):
        """Добавление нового заказа."""
        dialog = OrderDialog(self.root, "Добавить заказ")
        if dialog.result_data:
            # Проверяем уникальность номера
            order_number = dialog.result_data.get("order_number", "")
            if not order_number:
                messagebox.showerror("Ошибка", "Номер заказа обязателен!")
                return
            
            if find_order_by_number(order_number):
                messagebox.showerror("Ошибка", f"Заказ с номером {order_number} уже существует!")
                return
            
            if add_order(dialog.result_data):
                self._load_data()
                messagebox.showinfo("Успех", "Заказ успешно добавлен!")
            else:
                messagebox.showerror("Ошибка", "Не удалось сохранить заказ.")
    
    def _edit_order(self):
        """Редактирование выбранного заказа."""
        order = self._get_selected_order()
        if not order:
            messagebox.showwarning("Предупреждение", "Выберите заказ для редактирования!")
            return
        
        dialog = OrderDialog(self.root, "Редактировать заказ", order_data=order)
        if dialog.result_data:
            order_number = order.get("order_number")
            if update_order(order_number, dialog.result_data):
                self._load_data()
                messagebox.showinfo("Успех", "Заказ успешно обновлён!")
            else:
                messagebox.showerror("Ошибка", "Не удалось сохранить изменения.")
    
    def _delete_order(self):
        """Удаление выбранного заказа."""
        order = self._get_selected_order()
        if not order:
            messagebox.showwarning("Предупреждение", "Выберите заказ для удаления!")
            return
        
        order_number = order.get("order_number", "")
        confirm = messagebox.askyesno(
            "Подтверждение",
            f"Вы действительно хотите удалить заказ №{order_number}?"
        )
        
        if confirm:
            if delete_order(order_number):
                self._load_data()
                messagebox.showinfo("Успех", "Заказ удалён!")
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить заказ.")
    
    def _open_folder(self):
        """Открытие папки документа в Double Commander."""
        order = self._get_selected_order()
        if not order:
            messagebox.showwarning("Предупреждение", "Выберите заказ!")
            return
        
        folder_path = order.get("folder_path", "")
        if not folder_path:
            messagebox.showwarning("Предупреждение", "У заказа не указана папка!")
            return
        
        if not os.path.exists(folder_path):
            messagebox.showerror("Ошибка", f"Папка не найдена:\n{folder_path}")
            return
        
        if open_in_double_commander(folder_path):
            pass  # Успешно
        else:
            messagebox.showerror("Ошибка", "Не удалось открыть Double Commander.\nПроверьте настройки конфигурации.")
    
    def _search_customer(self):
        """Поиск информации о заказчике."""
        order = self._get_selected_order()
        if not order:
            messagebox.showwarning("Предупреждение", "Выберите заказ!")
            return
        
        customer = order.get("customer", "").strip()
        if not customer:
            messagebox.showwarning("Предупреждение", "У заказа не указан заказчик!")
            return
        
        search_on_site(customer)
    
    def _search_technologist(self):
        """Поиск информации о технологе."""
        order = self._get_selected_order()
        if not order:
            messagebox.showwarning("Предупреждение", "Выберите заказ!")
            return
        
        technologist = order.get("technologist", "").strip()
        if not technologist:
            messagebox.showwarning("Предупреждение", "У заказа не указан технолог!")
            return
        
        search_on_site(technologist)


def main():
    """Точка входа приложения."""
    root = tk.Tk()
    app = OrdersApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
