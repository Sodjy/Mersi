import logging
import sys
from PyQt6.QtWidgets import QMessageBox
from database import init_db
from sqlalchemy.orm import sessionmaker
from database.models import Notification

def setup_error_handler():
    """Настройка обработчика ошибок для приложения"""
    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='app_errors.log'
    )
    
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Обработчик неотловленных исключений"""
        logging.error("Uncaught exception", 
                     exc_info=(exc_type, exc_value, exc_traceback))
        QMessageBox.critical(
            None,
            "Критическая ошибка",
            f"Произошла ошибка:\n{str(exc_value)}\n\nПодробности в лог-файле."
        )
    
    # Устанавливаем глобальный обработчик исключений
    sys.excepthook = handle_exception

class NotificationManager:
    """Менеджер уведомлений для работы с БД"""
    def __init__(self):
        self.engine = init_db()
        self.Session = sessionmaker(bind=self.engine)
    
    def create_notification(self, message, notification_type, related_id=0, user_id=0):
        """Создание нового уведомления"""
        session = self.Session()
        notification = Notification(
            user_id=user_id,
            message=message,
            notification_type=notification_type,
            related_id=related_id
        )
        session.add(notification)
        session.commit()
        return notification
    
    def get_unread_notifications(self, user_id=0):
        """Получение непрочитанных уведомлений"""
        session = self.Session()
        notifications = session.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).order_by(Notification.created_at.desc()).all()
        return notifications
    
    def get_unread_count(self, user_id=0):
        """Получение количества непрочитанных уведомлений"""
        session = self.Session()
        count = session.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()
        return count
    
    def mark_as_read(self, notification_id):
        """Пометить уведомление как прочитанное"""
        session = self.Session()
        notification = session.query(Notification).get(notification_id)
        if notification:
            notification.is_read = True
            session.commit()
            return True
        return False
    
    def clear_all(self, user_id=0):
        """Удалить все уведомления пользователя"""
        session = self.Session()
        session.query(Notification).filter(
            Notification.user_id == user_id
        ).delete()
        session.commit()