from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from utils.notifications import NotificationManager

class NotificationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Уведомления")
        self.setGeometry(100, 100, 500, 400)
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Кнопки управления
        self.buttons_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.clicked.connect(self.load_notifications)
        self.mark_read_button = QPushButton("Пометить как прочитанные")
        self.mark_read_button.clicked.connect(self.mark_as_read)
        self.clear_button = QPushButton("Очистить все")
        self.clear_button.clicked.connect(self.clear_all)
        
        self.buttons_layout.addWidget(self.refresh_button)
        self.buttons_layout.addWidget(self.mark_read_button)
        self.buttons_layout.addWidget(self.clear_button)
        
        # Список уведомлений
        self.notification_list = QListWidget()
        
        # Компоновка
        self.layout.addLayout(self.buttons_layout)
        self.layout.addWidget(self.notification_list)
        
        # Менеджер уведомлений
        self.notification_manager = NotificationManager()
        
        # Загрузка уведомлений
        self.load_notifications()
    
    def load_notifications(self):
        self.notification_list.clear()
        notifications = self.notification_manager.get_unread_notifications()
        
        for notification in notifications:
            item_text = f"[{notification.created_at.strftime('%d.%m.%Y %H:%M')}] {notification.message}"
            item = self.notification_list.addItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, notification.id)
            if not notification.is_read:
                item.setBackground(Qt.GlobalColor.lightGray)
    
    def mark_as_read(self):
        selected_items = self.notification_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите уведомления для пометки как прочитанные")
            return
        
        for item in selected_items:
            notification_id = item.data(Qt.ItemDataRole.UserRole)
            if self.notification_manager.mark_as_read(notification_id):
                item.setBackground(Qt.GlobalColor.white)
    
    def clear_all(self):
        reply = QMessageBox.question(
            self, 'Подтверждение очистки',
            'Вы уверены, что хотите очистить все уведомления?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.notification_manager.clear_all()
            self.load_notifications()