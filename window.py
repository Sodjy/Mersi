import tkinter as tk
from tkinter import ttk, messagebox
import logging

class MainWindow:
    def __init__(self):
        """Инициализация главного окна приложения."""
        self.root = tk.Tk()
        self.root.title("MurphyLogistik")
        self.root.geometry("1000x700")  # Увеличенный размер для удобства
        self.root.minsize(800, 600)  # Минимальный размер окна
        
        # Настройка стилей
        self.setup_styles()
        
        # Создание виджетов
        self.create_widgets()
        
        # Настройка логгирования
        self.logger = logging.getLogger("MurphyLogistik")
        
    def setup_styles(self):
        """Настройка стилей для виджетов."""
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10), padding=5)
        
    def create_widgets(self):
        """Создание и размещение всех элементов интерфейса."""
        # Главный контейнер
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 1. Верхняя панель (заголовок)
        header = ttk.Label(
            main_frame, 
            text="Система логистики MurphyLogistik",
            font=("Arial", 16, "bold")
        )
        header.pack(pady=20)
        
        # 2. Панель навигации (кнопки)
        nav_frame = ttk.Frame(main_frame)
        nav_frame.pack(fill=tk.X, pady=10)
        
        buttons = [
            ("Заказы", self.show_orders),
            ("Транспорт", self.show_transport),
            ("Отчеты", self.show_reports),
            ("Настройки", self.show_settings)
        ]
        
        for text, command in buttons:
            btn = ttk.Button(nav_frame, text=text, command=command)
            btn.pack(side=tk.LEFT, padx=5)
        
        # 3. Основная рабочая область
        self.workspace = ttk.Frame(main_frame, relief=tk.SUNKEN, borderwidth=1)
        self.workspace.pack(fill=tk.BOTH, expand=True)
        
        # 4. Статус бар
        self.status_var = tk.StringVar()
        self.status_var.set("Готово")
        status_bar = ttk.Label(
            main_frame, 
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.pack(fill=tk.X, pady=(5, 0))
        
    def show_orders(self):
        """Показать раздел с заказами."""
        self.clear_workspace()
        label = ttk.Label(self.workspace, text="Раздел заказов в разработке")
        label.pack(pady=50)
        self.status_var.set("Работаем с заказами")
        
    def show_transport(self):
        """Показать раздел с транспортом."""
        self.clear_workspace()
        label = ttk.Label(self.workspace, text="Раздел транспорта в разработке")
        label.pack(pady=50)
        self.status_var.set("Управление транспортом")
        
    def show_reports(self):
        """Показать раздел с отчетами."""
        self.clear_workspace()
        label = ttk.Label(self.workspace, text="Раздел отчетов в разработке")
        label.pack(pady=50)
        self.status_var.set("Генерация отчетов")
        
    def show_settings(self):
        """Показать настройки."""
        self.clear_workspace()
        label = ttk.Label(self.workspace, text="Раздел настроек в разработке")
        label.pack(pady=50)
        self.status_var.set("Настройки системы")
        
    def clear_workspace(self):
        """Очистить рабочую область."""
        for widget in self.workspace.winfo_children():
            widget.destroy()
        
    def mainloop(self):
        """Запуск главного цикла приложения."""
        self.root.mainloop()

# Пример использования (для тестирования)
if __name__ == "__main__":
    window = MainWindow()
    window.mainloop()