from PyQt5.QtWidgets import QHeaderView
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView, QLineEdit, 
    QLabel, QFormLayout, QGroupBox, QMessageBox, QComboBox
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt
from database import init_db
from sqlalchemy.orm import sessionmaker
from database.models import Client
from utils.notifications import NotificationManager

class ClientForm(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Панель поиска и фильтрации
        self.search_group = QGroupBox("Поиск и фильтрация")
        self.search_layout = QHBoxLayout()
        self.search_group.setLayout(self.search_layout)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по названию, контакту или телефону...")
        self.search_input.textChanged.connect(self.load_clients)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Все", "Активные", "Архивные"])
        self.filter_combo.currentIndexChanged.connect(self.load_clients)
        
        self.search_layout.addWidget(QLabel("Поиск:"))
        self.search_layout.addWidget(self.search_input, 2)
        self.search_layout.addWidget(QLabel("Статус:"))
        self.search_layout.addWidget(self.filter_combo, 1)
        
        # Форма редактирования
        self.form_group = QGroupBox("Данные клиента")
        self.form_layout = QFormLayout()
        self.form_group.setLayout(self.form_layout)
        
        self.id_label = QLabel("Новый клиент")
        self.name_input = QLineEdit()
        self.contact_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.address_input = QLineEdit()
        
        self.form_layout.addRow("ID:", self.id_label)
        self.form_layout.addRow("Название компании:", self.name_input)
        self.form_layout.addRow("Контактное лицо:", self.contact_input)
        self.form_layout.addRow("Телефон:", self.phone_input)
        self.form_layout.addRow("Email:", self.email_input)
        self.form_layout.addRow("Адрес:", self.address_input)
        
        # Кнопки действий
        self.buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_client)
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.cancel_edit)
        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.delete_client)
        self.delete_button.setEnabled(False)
        
        self.buttons_layout.addWidget(self.save_button)
        self.buttons_layout.addWidget(self.cancel_button)
        self.buttons_layout.addWidget(self.delete_button)
        
        # Таблица клиентов
        self.table = QTableView()
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.table.doubleClicked.connect(self.load_client_data)
        
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels([
            "ID", "Название", "Контакт", "Телефон", "Email", "Адрес", "Статус"
        ])
        self.table.setModel(self.model)
       self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        
        # Компоновка
        self.layout.addWidget(self.search_group)
        self.layout.addWidget(self.form_group)
        self.layout.addLayout(self.buttons_layout)
        self.layout.addWidget(self.table)
        
        # Инициализация БД
        self.engine = init_db()
        self.Session = sessionmaker(bind=self.engine)
        self.current_id = None
        self.load_clients()
    
    def load_clients(self):
        session = self.Session()
        search_text = f"%{self.search_input.text()}%"
        status_filter = self.filter_combo.currentText()
        
        query = session.query(Client)
        
        if search_text != "%%":
            query = query.filter(
                (Client.name.ilike(search_text)) |
                (Client.contact_person.ilike(search_text)) |
                (Client.phone.ilike(search_text))
            )
        
        if status_filter == "Активные":
            query = query.filter(Client.is_active == True)
        elif status_filter == "Архивные":
            query = query.filter(Client.is_active == False)
        
        clients = query.order_by(Client.name).all()
        
        self.model.setRowCount(0)
        for row, client in enumerate(clients):
            self.model.insertRow(row)
            self.model.setItem(row, 0, QStandardItem(str(client.id)))
            self.model.setItem(row, 1, QStandardItem(client.name))
            self.model.setItem(row, 2, QStandardItem(client.contact_person or ""))
            self.model.setItem(row, 3, QStandardItem(client.phone or ""))
            self.model.setItem(row, 4, QStandardItem(client.email or ""))
            self.model.setItem(row, 5, QStandardItem(client.address or ""))
            self.model.setItem(row, 6, QStandardItem("Активный" if client.is_active else "Архивный"))
    
    def load_client_data(self, index):
        session = self.Session()
        client_id = int(self.model.item(index.row(), 0).text())
        client = session.query(Client).get(client_id)
        
        if client:
            self.current_id = client.id
            self.id_label.setText(str(client.id))
            self.name_input.setText(client.name or "")
            self.contact_input.setText(client.contact_person or "")
            self.phone_input.setText(client.phone or "")
            self.email_input.setText(client.email or "")
            self.address_input.setText(client.address or "")
            self.delete_button.setEnabled(True)
    
    def save_client(self):
        session = self.Session()
        
        if self.current_id:
            # Редактирование существующего клиента
            client = session.query(Client).get(self.current_id)
            if client:
                client.name = self.name_input.text()
                client.contact_person = self.contact_input.text()
                client.phone = self.phone_input.text()
                client.email = self.email_input.text()
                client.address = self.address_input.text()
                action = "обновлен"
        else:
            # Создание нового клиента
            client = Client(
                name=self.name_input.text(),
                contact_person=self.contact_input.text(),
                phone=self.phone_input.text(),
                email=self.email_input.text(),
                address=self.address_input.text()
            )
            session.add(client)
            action = "добавлен"
        
        session.commit()
        
        # Создание уведомления
        notification_manager = NotificationManager()
        notification_manager.create_notification(
            message=f"Клиент '{client.name}' {action}",
            notification_type="client",
            related_id=client.id
        )
        
        self.clear_fields()
        self.load_clients()
    
    def delete_client(self):
        if self.current_id:
            reply = QMessageBox.question(
                self, 'Подтверждение удаления',
                'Вы уверены, что хотите удалить этого клиента?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                session = self.Session()
                client = session.query(Client).get(self.current_id)
                if client:
                    # Создание уведомления перед удалением
                    notification_manager = NotificationManager()
                    notification_manager.create_notification(
                        message=f"Клиент '{client.name}' удален",
                        notification_type="client",
                        related_id=client.id
                    )
                    
                    session.delete(client)
                    session.commit()
                    self.clear_fields()
                    self.load_clients()
    
    def cancel_edit(self):
        self.clear_fields()
    
    def clear_fields(self):
        self.current_id = None
        self.id_label.setText("Новый клиент")
        self.name_input.clear()
        self.contact_input.clear()
        self.phone_input.clear()
        self.email_input.clear()
        self.address_input.clear()
        self.delete_button.setEnabled(False)