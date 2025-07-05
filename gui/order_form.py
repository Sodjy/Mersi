from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView, 
    QLineEdit, QLabel, QFormLayout, QGroupBox, QComboBox, QDateEdit, 
    QFileDialog, QMessageBox, QTabWidget
)
from PyQt6.QtCore import QDate
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from database import init_db
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from database.models import Order, Client, Carrier, Vehicle, Payment, Document
from utils.notifications import NotificationManager

class OrderForm(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Инициализация БД
        self.engine = init_db()
        self.Session = sessionmaker(bind=self.engine)
        
        # Вкладки
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        # Вкладка данных заказа
        self.order_tab = QWidget()
        self.order_tab_layout = QVBoxLayout()
        self.order_tab.setLayout(self.order_tab_layout)
        
        # Форма заказа
        self.order_group = QGroupBox("Данные заказа")
        self.order_layout = QFormLayout()
        self.order_group.setLayout(self.order_layout)
        
        # Выбор клиента
        self.client_combo = QComboBox()
        self.client_combo.currentIndexChanged.connect(self.load_client_data)
        
        # Выбор перевозчика
        self.carrier_combo = QComboBox()
        self.carrier_combo.currentIndexChanged.connect(self.load_carrier_data)
        
        # Выбор ТС
        self.vehicle_combo = QComboBox()
        
        # Адреса
        self.loading_address = QLineEdit()
        self.unloading_address = QLineEdit()
        
        # Груз
        self.cargo_name = QLineEdit()
        self.packaging = QLineEdit()
        self.weight = QLineEdit()
        self.loading_type = QComboBox()
        self.loading_type.addItems(["Верхняя", "Боковая", "Задняя"])
        
        # Даты
        self.order_date = QDateEdit()
        self.order_date.setDate(QDate.currentDate())
        self.loading_date = QDateEdit()
        self.loading_date.setDate(QDate.currentDate())
        
        # Статус
        self.status_combo = QComboBox()
        self.status_combo.addItems([
            "Создан", "В обработке", "Погрузка", "В пути", 
            "Выгрузка", "Завершен", "Отменен"
        ])
        
        # Кнопки
        self.buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Сохранить заказ")
        self.save_button.clicked.connect(self.save_order)
        self.delete_button = QPushButton("Удалить заказ")
        self.delete_button.clicked.connect(self.delete_order)
        self.delete_button.setEnabled(False)
        
        self.buttons_layout.addWidget(self.save_button)
        self.buttons_layout.addWidget(self.delete_button)
        
        # Добавление полей в форму
        self.order_layout.addRow("Клиент:", self.client_combo)
        self.order_layout.addRow("Перевозчик:", self.carrier_combo)
        self.order_layout.addRow("Транспортное средство:", self.vehicle_combo)
        self.order_layout.addRow("Адрес погрузки:", self.loading_address)
        self.order_layout.addRow("Адрес выгрузки:", self.unloading_address)
        self.order_layout.addRow("Наименование груза:", self.cargo_name)
        self.order_layout.addRow("Упаковка:", self.packaging)
        self.order_layout.addRow("Вес (кг):", self.weight)
        self.order_layout.addRow("Тип загрузки:", self.loading_type)
        self.order_layout.addRow("Дата заказа:", self.order_date)
        self.order_layout.addRow("Дата погрузки:", self.loading_date)
        self.order_layout.addRow("Статус:", self.status_combo)
        
        self.order_tab_layout.addWidget(self.order_group)
        self.order_tab_layout.addLayout(self.buttons_layout)
        
        # Вкладка платежей
        self.payments_tab = QWidget()
        self.payments_layout = QVBoxLayout()
        self.payments_tab.setLayout(self.payments_layout)
        
        self.payments_table = QTableView()
        self.payments_model = QStandardItemModel()
        self.payments_model.setHorizontalHeaderLabels([
            "Дата", "Сумма", "Тип", "Описание"
        ])
        self.payments_table.setModel(self.payments_model)
        
        self.profit_label = QLabel("Прибыль: 0.00 руб.")
        self.profit_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        self.payment_form = QGroupBox("Добавить платеж")
        self.payment_form_layout = QFormLayout()
        self.payment_form.setLayout(self.payment_form_layout)
        
        self.payment_amount = QLineEdit()
        self.payment_date = QDateEdit()
        self.payment_date.setDate(QDate.currentDate())
        self.payment_type = QComboBox()
        self.payment_type.addItems(["От клиента", "Перевозчику"])
        self.payment_description = QLineEdit()
        self.add_payment_button = QPushButton("Добавить платеж")
        self.add_payment_button.clicked.connect(self.add_payment)
        
        self.payment_form_layout.addRow("Сумма:", self.payment_amount)
        self.payment_form_layout.addRow("Дата:", self.payment_date)
        self.payment_form_layout.addRow("Тип:", self.payment_type)
        self.payment_form_layout.addRow("Описание:", self.payment_description)
        self.payment_form_layout.addRow(self.add_payment_button)
        
        self.payments_layout.addWidget(self.payments_table)
        self.payments_layout.addWidget(self.payment_form)
        self.payments_layout.addWidget(self.profit_label)
        
        # Вкладка документов
        self.documents_tab = QWidget()
        self.documents_layout = QVBoxLayout()
        self.documents_tab.setLayout(self.documents_layout)
        
        self.documents_table = QTableView()
        self.documents_model = QStandardItemModel()
        self.documents_model.setHorizontalHeaderLabels([
            "Название", "Описание", "Путь"
        ])
        self.documents_table.setModel(self.documents_model)
        
        self.document_form = QGroupBox("Добавить документ")
        self.document_form_layout = QFormLayout()
        self.document_form.setLayout(self.document_form_layout)
        
        self.document_name = QLineEdit()
        self.document_description = QLineEdit()
        self.document_path = QLineEdit()
        self.document_path.setReadOnly(True)
        self.browse_button = QPushButton("Обзор...")
        self.browse_button.clicked.connect(self.browse_document)
        self.add_document_button = QPushButton("Добавить документ")
        self.add_document_button.clicked.connect(self.add_document)
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.document_path)
        path_layout.addWidget(self.browse_button)
        
        self.document_form_layout.addRow("Название:", self.document_name)
        self.document_form_layout.addRow("Описание:", self.document_description)
        self.document_form_layout.addRow("Файл:", path_layout)
        self.document_form_layout.addRow(self.add_document_button)
        
        self.documents_layout.addWidget(self.documents_table)
        self.documents_layout.addWidget(self.document_form)
        
        # Добавление вкладок
        self.tabs.addTab(self.order_tab, "Данные заказа")
        self.tabs.addTab(self.payments_tab, "Платежи")
        self.tabs.addTab(self.documents_tab, "Документы")
        
        # Загрузка данных
        self.load_clients()
        self.load_carriers()
        self.current_order_id = None
    
    def load_clients(self):
        session = self.Session()
        clients = session.query(Client).order_by(Client.name).all()
        self.client_combo.clear()
        for client in clients:
            self.client_combo.addItem(client.name, client.id)
    
    def load_carriers(self):
        session = self.Session()
        carriers = session.query(Carrier).order_by(Carrier.company_name).all()
        self.carrier_combo.clear()
        for carrier in carriers:
            self.carrier_combo.addItem(carrier.company_name, carrier.id)
    
    def load_carrier_data(self):
        carrier_id = self.carrier_combo.currentData()
        if carrier_id:
            session = self.Session()
            vehicles = session.query(Vehicle).filter_by(carrier_id=carrier_id).all()
            self.vehicle_combo.clear()
            for vehicle in vehicles:
                self.vehicle_combo.addItem(f"{vehicle.plate_number} ({vehicle.model})", vehicle.id)
    
    def load_client_data(self):
        # Можно добавить дополнительную логику при необходимости
        pass
    
    def save_order(self):
        session = self.Session()
        
        if self.current_order_id:
            # Редактирование существующего заказа
            order = session.query(Order).get(self.current_order_id)
            if order:
                order.client_id = self.client_combo.currentData()
                order.carrier_id = self.carrier_combo.currentData()
                order.vehicle_id = self.vehicle_combo.currentData()
                order.loading_address = self.loading_address.text()
                order.unloading_address = self.unloading_address.text()
                order.cargo_name = self.cargo_name.text()
                order.packaging = self.packaging.text()
                order.weight = float(self.weight.text()) if self.weight.text() else 0.0
                order.loading_type = self.loading_type.currentText()
                order.order_date = self.order_date.date().toPyDate()
                order.loading_date = self.loading_date.date().toPyDate()
                order.status = self.status_combo.currentText()
                action = "обновлен"
        else:
            # Создание нового заказа
            order = Order(
                client_id=self.client_combo.currentData(),
                carrier_id=self.carrier_combo.currentData(),
                vehicle_id=self.vehicle_combo.currentData(),
                loading_address=self.loading_address.text(),
                unloading_address=self.unloading_address.text(),
                cargo_name=self.cargo_name.text(),
                packaging=self.packaging.text(),
                weight=float(self.weight.text()) if self.weight.text() else 0.0,
                loading_type=self.loading_type.currentText(),
                order_date=self.order_date.date().toPyDate(),
                loading_date=self.loading_date.date().toPyDate(),
                status=self.status_combo.currentText()
            )
            session.add(order)
            action = "создан"
        
        session.commit()
        
        if not self.current_order_id:
            self.current_order_id = order.id
            self.delete_button.setEnabled(True)
        
        # Создание уведомления
        notification_manager = NotificationManager()
        notification_manager.create_notification(
            message=f"Заказ #{order.id} {action}: {order.cargo_name}",
            notification_type="order",
            related_id=order.id
        )
        
        self.load_payments()
        self.load_documents()
        self.calculate_profit()
    
    def delete_order(self):
        if self.current_order_id:
            reply = QMessageBox.question(
                self, 'Подтверждение удаления',
                'Вы уверены, что хотите удалить этот заказ?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                session = self.Session()
                order = session.query(Order).get(self.current_order_id)
                if order:
                    # Создание уведомления перед удалением
                    notification_manager = NotificationManager()
                    notification_manager.create_notification(
                        message=f"Заказ #{order.id} удален: {order.cargo_name}",
                        notification_type="order",
                        related_id=order.id
                    )
                    
                    session.delete(order)
                    session.commit()
                    self.clear_fields()
    
    def clear_fields(self):
        self.current_order_id = None
        self.client_combo.setCurrentIndex(0)
        self.carrier_combo.setCurrentIndex(0)
        self.vehicle_combo.clear()
        self.loading_address.clear()
        self.unloading_address.clear()
        self.cargo_name.clear()
        self.packaging.clear()
        self.weight.clear()
        self.loading_type.setCurrentIndex(0)
        self.order_date.setDate(QDate.currentDate())
        self.loading_date.setDate(QDate.currentDate())
        self.status_combo.setCurrentIndex(0)
        self.delete_button.setEnabled(False)
        
        self.payments_model.setRowCount(0)
        self.documents_model.setRowCount(0)
        self.profit_label.setText("Прибыль: 0.00 руб.")
    
    def add_payment(self):
        if not self.current_order_id:
            QMessageBox.warning(self, "Ошибка", "Сначала сохраните заказ")
            return
        
        try:
            amount = float(self.payment_amount.text())
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректную сумму")
            return
        
        session = self.Session()
        payment = Payment(
            order_id=self.current_order_id,
            amount=amount,
            payment_date=self.payment_date.date().toPyDate(),
            is_client_payment=(self.payment_type.currentIndex() == 0),
            description=self.payment_description.text()
        )
        session.add(payment)
        session.commit()
        
        # Создание уведомления
        notification_manager = NotificationManager()
        payment_type = "от клиента" if payment.is_client_payment else "перевозчику"
        notification_manager.create_notification(
            message=f"Платеж {amount:.2f} руб. ({payment_type}) по заказу #{self.current_order_id}",
            notification_type="payment",
            related_id=self.current_order_id
        )
        
        self.payment_amount.clear()
        self.payment_description.clear()
        self.load_payments()
        self.calculate_profit()
    
    def load_payments(self):
        if not self.current_order_id:
            return
        
        session = self.Session()
        payments = session.query(Payment).filter_by(order_id=self.current_order_id).all()
        
        self.payments_model.setRowCount(0)
        for row, payment in enumerate(payments):
            self.payments_model.insertRow(row)
            self.payments_model.setItem(row, 0, QStandardItem(str(payment.payment_date)))
            self.payments_model.setItem(row, 1, QStandardItem(f"{payment.amount:.2f} руб."))
            self.payments_model.setItem(row, 2, QStandardItem("От клиента" if payment.is_client_payment else "Перевозчику"))
            self.payments_model.setItem(row, 3, QStandardItem(payment.description or ""))
    
    def calculate_profit(self):
        if not self.current_order_id:
            return
        
        session = self.Session()
        client_payments = session.query(func.sum(Payment.amount)).filter(
            Payment.order_id == self.current_order_id,
            Payment.is_client_payment == True
        ).scalar() or 0
        
        carrier_payments = session.query(func.sum(Payment.amount)).filter(
            Payment.order_id == self.current_order_id,
            Payment.is_client_payment == False
        ).scalar() or 0
        
        profit = client_payments - carrier_payments
        self.profit_label.setText(f"Прибыль: {profit:.2f} руб.")
    
    def browse_document(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите документ", "", "Все файлы (*);;PDF (*.pdf);;Изображения (*.png *.jpg)"
        )
        
        if file_path:
            self.document_path.setText(file_path)
    
    def add_document(self):
        if not self.current_order_id:
            QMessageBox.warning(self, "Ошибка", "Сначала сохраните заказ")
            return
        
        if not self.document_path.text():
            QMessageBox.warning(self, "Ошибка", "Выберите файл")
            return
        
        session = self.Session()
        document = Document(
            order_id=self.current_order_id,
            name=self.document_name.text(),
            file_path=self.document_path.text(),
            description=self.document_description.text()
        )
        session.add(document)
        session.commit()
        
        # Создание уведомления
        notification_manager = NotificationManager()
        notification_manager.create_notification(
            message=f"Документ '{document.name}' добавлен к заказу #{self.current_order_id}",
            notification_type="document",
            related_id=self.current_order_id
        )
        
        self.document_name.clear()
        self.document_description.clear()
        self.document_path.clear()
        self.load_documents()
    
    def load_documents(self):
        if not self.current_order_id:
            return
        
        session = self.Session()
        documents = session.query(Document).filter_by(order_id=self.current_order_id).all()
        
        self.documents_model.setRowCount(0)
        for row, document in enumerate(documents):
            self.documents_model.insertRow(row)
            self.documents_model.setItem(row, 0, QStandardItem(document.name))
            self.documents_model.setItem(row, 1, QStandardItem(document.description or ""))
            self.documents_model.setItem(row, 2, QStandardItem(document.file_path))