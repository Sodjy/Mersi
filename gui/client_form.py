from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView, QLineEdit,
    QLabel, QFormLayout, QGroupBox, QMessageBox, QComboBox, QHeaderView
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
        self.setWindowTitle("Управление клиентами")
        self.resize(800, 600)
        self._setup_ui()
        self._setup_db()
        self.load_clients()

    def _setup_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # 1. Панель поиска и фильтрации
        self._setup_search_panel()
        
        # 2. Форма редактирования клиента
        self._setup_edit_form()
        
        # 3. Панель кнопок действий
        self._setup_action_buttons()
        
        # 4. Таблица клиентов
        self._setup_clients_table()

    def _setup_search_panel(self):
        """Настройка панели поиска"""
        self.search_group = QGroupBox("Поиск и фильтрация")
        self.search_layout = QHBoxLayout()
        
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
        
        self.search_group.setLayout(self.search_layout)
        self.layout.addWidget(self.search_group)

    def _setup_edit_form(self):
        """Настройка формы редактирования"""
        self.form_group = QGroupBox("Данные клиента")
        self.form_layout = QFormLayout()
        
        self.id_label = QLabel("Новый клиент")
        self.name_input = QLineEdit()
        self.contact_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.phone_input.setInputMask("+7(999)999-99-99;_")
        self.email_input = QLineEdit()
        self.address_input = QLineEdit()
        
        self.form_layout.addRow("ID:", self.id_label)
        self.form_layout.addRow("Название компании:", self.name_input)
        self.form_layout.addRow("Контактное лицо:", self.contact_input)
        self.form_layout.addRow("Телефон:", self.phone_input)
        self.form_layout.addRow("Email:", self.email_input)
        self.form_layout.addRow("Адрес:", self.address_input)
        
        self.form_group.setLayout(self.form_layout)
        self.layout.addWidget(self.form_group)

    def _setup_action_buttons(self):
        """Настройка кнопок действий"""
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
        
        self.layout.addLayout(self.buttons_layout)

    def _setup_clients_table(self):
        """Настройка таблицы клиентов"""
        self.table = QTableView()
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.table.doubleClicked.connect(self.load_client_data)
        
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels([
            "ID", "Название", "Контакт", "Телефон", "Email", "Адрес", "Статус"
        ])
        self.table.setModel(self.model)
        
        # Настройка растягивания колонок
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        
        self.layout.addWidget(self.table)

    def _setup_db(self):
        """Инициализация подключения к БД"""
        self.engine = init_db()
        self.Session = sessionmaker(bind=self.engine)
        self.current_id = None

    def load_clients(self):
        """Загрузка списка клиентов из БД"""
        session = self.Session()
        try:
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
                self._add_client_to_table(row, client)
                
        finally:
            session.close()

    def _add_client_to_table(self, row, client):
        """Добавление клиента в таблицу"""
        self.model.insertRow(row)
        self.model.setItem(row, 0, QStandardItem(str(client.id)))
        self.model.setItem(row, 1, QStandardItem(client.name))
        self.model.setItem(row, 2, QStandardItem(client.contact_person or ""))
        self.model.setItem(row, 3, QStandardItem(client.phone or ""))
        self.model.setItem(row, 4, QStandardItem(client.email or ""))
        self.model.setItem(row, 5, QStandardItem(client.address or ""))
        self.model.setItem(row, 6, QStandardItem("Активный" if client.is_active else "Архивный"))

    def load_client_data(self, index):
        """Загрузка данных выбранного клиента в форму"""
        session = self.Session()
        try:
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
        finally:
            session.close()

    def save_client(self):
        """Сохранение клиента в БД"""
        if not self._validate_inputs():
            return
            
        session = self.Session()
        try:
            if self.current_id:
                client = session.query(Client).get(self.current_id)
                action = "обновлен"
            else:
                client = Client()
                action = "добавлен"
            
            self._update_client_from_form(client)
            session.add(client)
            session.commit()
            
            self._notify_client_action(client, action)
            self.clear_fields()
            self.load_clients()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить клиента: {str(e)}")
            session.rollback()
        finally:
            session.close()

    def _validate_inputs(self):
        """Проверка введенных данных"""
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Ошибка", "Название компании обязательно для заполнения")
            return False
        return True

    def _update_client_from_form(self, client):
        """Обновление данных клиента из формы"""
        client.name = self.name_input.text().strip()
        client.contact_person = self.contact_input.text().strip()
        client.phone = self.phone_input.text().strip()
        client.email = self.email_input.text().strip()
        client.address = self.address_input.text().strip()
        client.is_active = True

    def _notify_client_action(self, client, action):
        """Создание уведомления о действии с клиентом"""
        notification_manager = NotificationManager()
        notification_manager.create_notification(
            message=f"Клиент '{client.name}' {action}",
            notification_type="client",
            related_id=client.id
        )

    def delete_client(self):
        """Удаление клиента из БД"""
        if not self.current_id:
            return
            
        reply = QMessageBox.question(
            self, 'Подтверждение удаления',
            'Вы уверены, что хотите удалить этого клиента?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.No:
            return
            
        session = self.Session()
        try:
            client = session.query(Client).get(self.current_id)
            if client:
                client_name = client.name
                session.delete(client)
                session.commit()
                
                self._notify_client_action(client, "удален")
                self.clear_fields()
                self.load_clients()
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить клиента: {str(e)}")
            session.rollback()
        finally:
            session.close()

    def cancel_edit(self):
        """Отмена редактирования"""
        self.clear_fields()

    def clear_fields(self):
        """Очистка полей формы"""
        self.current_id = None
        self.id_label.setText("Новый клиент")
        self.name_input.clear()
        self.contact_input.clear()
        self.phone_input.clear()
        self.email_input.clear()
        self.address_input.clear()
        self.delete_button.setEnabled(False)