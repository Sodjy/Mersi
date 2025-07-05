from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableView, QHBoxLayout, QPushButton, 
    QGroupBox, QFormLayout, QDateEdit, QComboBox, QLabel, QMessageBox
)
from PyQt6.QtCore import QDate
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from database import init_db
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from database.models import Payment, Order, Client
from utils.notifications import NotificationManager

class PaymentForm(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Фильтры
        self.filter_group = QGroupBox("Фильтры")
        self.filter_layout = QFormLayout()
        self.filter_group.setLayout(self.filter_layout)
        
        self.client_combo = QComboBox()
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.apply_button = QPushButton("Применить")
        self.apply_button.clicked.connect(self.load_payments)
        
        self.filter_layout.addRow("Клиент:", self.client_combo)
        self.filter_layout.addRow("Дата с:", self.date_from)
        self.filter_layout.addRow("Дата по:", self.date_to)
        self.filter_layout.addRow(self.apply_button)
        
        # Таблица платежей
        self.table = QTableView()
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels([
            "ID", "Дата", "Заказ", "Клиент", "Сумма", "Тип", "Описание"
        ])
        self.table.setModel(self.model)
        
        # Итоги
        self.summary_label = QLabel("Итого: 0.00 руб.")
        self.summary_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        # Компоновка
        self.layout.addWidget(self.filter_group)
        self.layout.addWidget(self.table)
        self.layout.addWidget(self.summary_label)
        
        # Инициализация БД
        self.engine = init_db()
        self.Session = sessionmaker(bind=self.engine)
        self.load_clients()
        self.load_payments()
    
    def load_clients(self):
        session = self.Session()
        clients = session.query(Client).order_by(Client.name).all()
        self.client_combo.addItem("Все клиенты", 0)
        for client in clients:
            self.client_combo.addItem(client.name, client.id)
    
    def load_payments(self):
        session = self.Session()
        
        query = session.query(Payment).join(Order).join(Client)
        
        client_id = self.client_combo.currentData()
        if client_id:
            query = query.filter(Order.client_id == client_id)
        
        date_from = self.date_from.date().toPyDate()
        date_to = self.date_to.date().toPyDate()
        query = query.filter(Payment.payment_date >= date_from, Payment.payment_date <= date_to)
        
        payments = query.order_by(Payment.payment_date.desc()).all()
        
        self.model.setRowCount(0)
        total = 0
        
        for row, payment in enumerate(payments):
            self.model.insertRow(row)
            self.model.setItem(row, 0, QStandardItem(str(payment.id)))
            self.model.setItem(row, 1, QStandardItem(str(payment.payment_date)))
            self.model.setItem(row, 2, QStandardItem(f"Заказ #{payment.order_id}"))
            self.model.setItem(row, 3, QStandardItem(payment.order.client.name))
            self.model.setItem(row, 4, QStandardItem(f"{payment.amount:.2f} руб."))
            self.model.setItem(row, 5, QStandardItem("От клиента" if payment.is_client_payment else "Перевозчику"))
            self.model.setItem(row, 6, QStandardItem(payment.description or ""))
            
            total += payment.amount if payment.is_client_payment else -payment.amount
        
        self.summary_label.setText(f"Итоговая прибыль: {total:.2f} руб.")