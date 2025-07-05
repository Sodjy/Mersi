import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.config import load_config
from utils.notifications import setup_error_handler  # Теперь импорт будет работать
from database.models import Base
from sqlalchemy import create_engine

def main():
    # Настройка обработки ошибок
    setup_error_handler()
    
    try:
        # Загрузка конфигурации
        config = load_config()
        
        # Инициализация БД
        engine = create_engine(config['database']['url'])
        Base.metadata.create_all(engine)
        
        # Создание приложения
        app = QApplication(sys.argv)
        window = MainWindow(engine)
        window.show()
        
        sys.exit(app.exec())
        
    except Exception as e:
        # Эта ошибка будет перехвачена setup_error_handler
        raise e

if __name__ == "__main__":
    main()