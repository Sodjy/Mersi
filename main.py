import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from database import init_db
from utils.background_tasks import BackgroundTaskManager

if __name__ == "__main__":
    # Инициализация базы данных
    init_db()
    
    # Запуск фоновых задач
    task_manager = BackgroundTaskManager()
    
    app = QApplication(sys.argv)
    
    # Загрузка стилей
    try:
        with open('styles/styles.css', 'r') as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("Файл стилей не найден")
    
    window = MainWindow()
    window.show()
    
    # Остановка фоновых задач при закрытии приложения
    app.aboutToQuit.connect(task_manager.stop)
    
    sys.exit(app.exec())