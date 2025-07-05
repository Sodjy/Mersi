import threading
import time
from datetime import datetime, timedelta
from database import init_db
from sqlalchemy.orm import sessionmaker
from database.models import Order, Payment
from utils.notifications import NotificationManager

class BackgroundTaskManager:
    def __init__(self):
        self.engine = init_db()
        self.Session = sessionmaker(bind=self.engine)
        self.running = True
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()
    
    def run(self):
        while self.running:
            try:
                self.check_overdue_payments()
                self.check_upcoming_orders()
                time.sleep(3600)  # Проверка каждый час
            except Exception as e:
                print(f"Ошибка в фоновой задаче: {str(e)}")
    
    def check_overdue_payments(self):
        session = self.Session()
        overdue_date = datetime.now().date() - timedelta(days=3)
        
        # Платежи от клиентов, которые просрочены
        overdue_payments = session.query(Payment).filter(
            Payment.is_client_payment == True,
            Payment.payment_date < overdue_date,
            Payment.order.has(Order.status.notin_(["Завершен", "Отменен"]))
        ).all()
        
        notification_manager = NotificationManager()
        for payment in overdue_payments:
            message = f"Просрочен платеж по заказу #{payment.order_id} ({payment.amount} руб.)"
            notification_manager.create_notification(
                message=message,
                notification_type="payment",
                related_id=payment.order_id
            )
    
    def check_upcoming_orders(self):
        session = self.Session()
        tomorrow = datetime.now().date() + timedelta(days=1)
        
        # Заказы на завтра
        upcoming_orders = session.query(Order).filter(
            Order.loading_date == tomorrow,
            Order.status.in_(["Создан", "В обработке"])
        ).all()
        
        notification_manager = NotificationManager()
        for order in upcoming_orders:
            message = f"На завтра запланирована погрузка по заказу #{order.id}"
            notification_manager.create_notification(
                message=message,
                notification_type="order",
                related_id=order.id
            )
    
    def stop(self):
        self.running = False
        self.thread.join()