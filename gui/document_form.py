from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableView, QHBoxLayout, QPushButton, 
    QGroupBox, QFormLayout, QLineEdit, QComboBox, QFileDialog,
    QLabel, QMessageBox
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from database import init_db
from sqlalchemy.orm import sessionmaker
from database.models import Document, Order, Client
from utils.notifications import NotificationManager

class DocumentForm(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Фильтры
        self.filter_group = QGroupBox("Фильтры")
        self.filter_layout = QFormLayout()
        self.filter_group.setLayout(self.filter_layout)
        
        self.client_combo = QComboBox()
        self.order_combo = QComboBox()
        self.apply_button = QPushButton("Применить")
        self.apply_button.clicked.connect(self.load_documents)
        
        self.filter_layout.addRow("Клиент:", self.client_combo)
        self.filter_layout.addRow("Заказ:", self.order_combo)
        self.filter_layout.addRow(self.apply_button)
        
        # Таблица документов
        self.table = QTableView()
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels([
            "ID", "Заказ", "Клиент", "Название", "Описание", "Путь"
        ])
        self.table.setModel(self.model)
        
        # Кнопки действий
        self.buttons_layout = QHBoxLayout()
        self.view_button = QPushButton("Просмотреть")
        self.view_button.clicked.connect(self.view_document)
        self.download_button = QPushButton("Скачать")
        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.delete_document)
        
        self.buttons_layout.addWidget(self.view_button)
        self.buttons_layout.addWidget(self.download_button)
        self.buttons_layout.addWidget(self.delete_button)
        
        # Компоновка
        self.layout.addWidget(self.filter_group)
        self.layout.addWidget(self.table)
        self.layout.addLayout(self.buttons_layout)
        
        # Инициализация БД
        self.engine = init_db()
        self.Session = sessionmaker(bind=self.engine)
        self.load_clients()
        self.load_documents()
    
    def load_clients(self):
        session = self.Session()
        clients = session.query(Client).order_by(Client.name).all()
        self.client_combo.addItem("Все клиенты", 0)
        for client in clients:
            self.client_combo.addItem(client.name, client.id)
        self.client_combo.currentIndexChanged.connect(self.load_orders)
    
    def load_orders(self):
        client_id = self.client_combo.currentData()
        if not client_id:
            return
        
        session = self.Session()
        self.order_combo.clear()
        self.order_combo.addItem("Все заказы", 0)
        
        orders = session.query(Order).filter_by(client_id=client_id).all()
        for order in orders:
            self.order_combo.addItem(f"Заказ #{order.id} - {order.cargo_name}", order.id)
    
    def load_documents(self):
        session = self.Session()
        
        query = session.query(Document).join(Order).join(Client)
        
        client_id = self.client_combo.currentData()
        if client_id:
            query = query.filter(Order.client_id == client_id)
        
        order_id = self.order_combo.currentData()
        if order_id:
            query = query.filter(Document.order_id == order_id)
        
        documents = query.order_by(Document.id.desc()).all()
        
        self.model.setRowCount(0)
        for row, document in enumerate(documents):
            self.model.insertRow(row)
            self.model.setItem(row, 0, QStandardItem(str(document.id)))
            self.model.setItem(row, 1, QStandardItem(f"Заказ #{document.order_id}"))
            self.model.setItem(row, 2, QStandardItem(document.order.client.name))
            self.model.setItem(row, 3, QStandardItem(document.name))
            self.model.setItem(row, 4, QStandardItem(document.description or ""))
            self.model.setItem(row, 5, QStandardItem(document.file_path))
    
    def view_document(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите документ для просмотра")
            return
        
        document_id = self.model.item(selected[0].row(), 0).text()
        session = self.Session()
        document = session.query(Document).get(int(document_id))
        
        if document:
            # В реальном приложении здесь был бы код для открытия файла
            QMessageBox.information(
                self, 
                "Просмотр документа", 
                f"Документ: {document.name}\nПуть: {document.file_path}"
            )
    
    def delete_document(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите документ для удаления")
            return
        
        document_id = self.model.item(selected[0].row(), 0).text()
        
        reply = QMessageBox.question(
            self, 'Подтверждение удаления',
            'Вы уверены, что хотите удалить этот документ?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            session = self.Session()
            document = session.query(Document).get(int(document_id))
            if document:
                # Создание уведомления перед удалением
                notification_manager = NotificationManager()
                notification_manager.create_notification(
                    message=f"Документ '{document.name}' удален из заказа #{document.order_id}",
                    notification_type="document",
                    related_id=document.order_id
                )
                
                session.delete(document)
                session.commit()
                self.load_documents()