from database import init_db
from sqlalchemy.orm import sessionmaker
from database.models import Notification

class NotificationManager:
    def __init__(self):
        self.engine = init_db()
        self.Session = sessionmaker(bind=self.engine)
    
    def create_notification(self, message, notification_type, related_id=0, user_id=0):
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
        session = self.Session()
        notifications = session.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).order_by(Notification.created_at.desc()).all()
        return notifications
    
    def get_unread_count(self, user_id=0):
        session = self.Session()
        count = session.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()
        return count
    
    def mark_as_read(self, notification_id):
        session = self.Session()
        notification = session.query(Notification).get(notification_id)
        if notification:
            notification.is_read = True
            session.commit()
            return True
        return False
    
    def clear_all(self, user_id=0):
        session = self.Session()
        session.query(Notification).filter(
            Notification.user_id == user_id
        ).delete()
        session.commit()