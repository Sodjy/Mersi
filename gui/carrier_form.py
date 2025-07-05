from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView, QLineEdit, 
    QLabel, QFormLayout, QGroupBox, QMessageBox, QComboBox
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt
from database import init_db
from sqlalchemy.orm import sessionmaker
from database.models import Carrier, Vehicle, Driver
from utils.notifications import NotificationManager

class CarrierForm(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Панель поиска
        self.search_group = QGroupBox("Поиск перевозчиков")
        self.search_layout = QHBoxLayout()
        self.search_group.setLayout(self.search_layout)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по названию компании...")
        self.search_input.textChanged.connect(self.load_carriers)
        
        self.search_layout.addWidget(QLabel("Поиск:"))
        self.search_layout.addWidget(self.search_input)
        
        # Форма перевозчика
        self.form_group = QGroupBox("Данные перевозчика")
        self.form_layout = QFormLayout()
        self.form_group.setLayout(self.form_layout)
        
        self.id_label = QLabel("Новый перевозчик")
        self.company_input = QLineEdit()
        self.contact_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        
        self.form_layout.addRow("ID:", self.id_label)
        self.form_layout.addRow("Название компании:", self.company_input)
        self.form_layout.addRow("Контактное лицо:", self.contact_input)
        self.form_layout.addRow("Телефон:", self.phone_input)
        self.form_layout.addRow("Email:", self.email_input)
        
        # Форма ТС
        self.vehicle_group = QGroupBox("Транспортное средство")
        self.vehicle_layout = QFormLayout()
        self.vehicle_group.setLayout(self.vehicle_layout)
        
        self.vehicle_plate = QLineEdit()
        self.vehicle_model = QLineEdit()
        self.vehicle_capacity = QLineEdit()
        
        self.vehicle_layout.addRow("Гос. номер:", self.vehicle_plate)
        self.vehicle_layout.addRow("Модель:", self.vehicle_model)
        self.vehicle_layout.addRow("Грузоподъемность (т):", self.vehicle_capacity)
        
        # Форма водителя
        self.driver_group = QGroupBox("Водитель")
        self.driver_layout = QFormLayout()
        self.driver_group.setLayout(self.driver_layout)
        
        self.driver_name = QLineEdit()
        self.driver_license = QLineEdit()
        self.driver_phone = QLineEdit()
        
        self.driver_layout.addRow("ФИО:", self.driver_name)
        self.driver_layout.addRow("Номер в/у:", self.driver_license)
        self.driver_layout.addRow("Телефон:", self.driver_phone)
        
        # Кнопки
        self.buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_carrier)
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.cancel_edit)
        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.delete_carrier)
        self.delete_button.setEnabled(False)
        
        self.buttons_layout.addWidget(self.save_button)
        self.buttons_layout.addWidget(self.cancel_button)
        self.buttons_layout.addWidget(self.delete_button)
        
        # Таблица перевозчиков
        self.table = QTableView()
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.table.doubleClicked.connect(self.load_carrier_data)
        
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels([
            "ID", "Компания", "Контакт", "Телефон", "Email", "ТС", "Водитель"
        ])
        self.table.setModel(self.model)
        self.table.horizontalHeader().setSectionResizeMode(1, QTableView.ResizeMode.Stretch)
        
        # Компоновка
        self.layout.addWidget(self.search_group)
        self.layout.addWidget(self.form_group)
        self.layout.addWidget(self.vehicle_group)
        self.layout.addWidget(self.driver_group)
        self.layout.addLayout(self.buttons_layout)
        self.layout.addWidget(self.table)
        
        # Инициализация БД
        self.engine = init_db()
        self.Session = sessionmaker(bind=self.engine)
        self.current_id = None
        self.load_carriers()
    
    def load_carriers(self):
        session = self.Session()
        search_text = f"%{self.search_input.text()}%"
        
        carriers = session.query(Carrier).filter(
            Carrier.company_name.ilike(search_text)
        ).order_by(Carrier.company_name).all()
        
        self.model.setRowCount(0)
        for row, carrier in enumerate(carriers):
            self.model.insertRow(row)
            self.model.setItem(row, 0, QStandardItem(str(carrier.id)))
            self.model.setItem(row, 1, QStandardItem(carrier.company_name))
            self.model.setItem(row, 2, QStandardItem(carrier.contact_person or ""))
            self.model.setItem(row, 3, QStandardItem(carrier.phone or ""))
            self.model.setItem(row, 4, QStandardItem(carrier.email or ""))
            
            # Информация о ТС и водителе
            vehicle_info = ""
            driver_info = ""
            if carrier.vehicles:
                vehicle = carrier.vehicles[0]
                vehicle_info = f"{vehicle.plate_number} ({vehicle.model})"
                if vehicle.driver:
                    driver_info = vehicle.driver.full_name
            
            self.model.setItem(row, 5, QStandardItem(vehicle_info))
            self.model.setItem(row, 6, QStandardItem(driver_info))
    
    def load_carrier_data(self, index):
        session = self.Session()
        carrier_id = int(self.model.item(index.row(), 0).text())
        carrier = session.query(Carrier).get(carrier_id)
        
        if carrier:
            self.current_id = carrier.id
            self.id_label.setText(str(carrier.id))
            self.company_input.setText(carrier.company_name or "")
            self.contact_input.setText(carrier.contact_person or "")
            self.phone_input.setText(carrier.phone or "")
            self.email_input.setText(carrier.email or "")
            
            # Загрузка ТС и водителя
            if carrier.vehicles:
                vehicle = carrier.vehicles[0]
                self.vehicle_plate.setText(vehicle.plate_number or "")
                self.vehicle_model.setText(vehicle.model or "")
                self.vehicle_capacity.setText(str(vehicle.capacity) if vehicle.capacity else "")
                
                if vehicle.driver:
                    driver = vehicle.driver
                    self.driver_name.setText(driver.full_name or "")
                    self.driver_license.setText(driver.license_number or "")
                    self.driver_phone.setText(driver.phone or "")
            
            self.delete_button.setEnabled(True)
    
    def save_carrier(self):
        session = self.Session()
        
        if self.current_id:
            # Редактирование существующего перевозчика
            carrier = session.query(Carrier).get(self.current_id)
            if carrier:
                carrier.company_name = self.company_input.text()
                carrier.contact_person = self.contact_input.text()
                carrier.phone = self.phone_input.text()
                carrier.email = self.email_input.text()
                action = "обновлен"
        else:
            # Создание нового перевозчика
            carrier = Carrier(
                company_name=self.company_input.text(),
                contact_person=self.contact_input.text(),
                phone=self.phone_input.text(),
                email=self.email_input.text()
            )
            session.add(carrier)
            action = "добавлен"
        
        # Сохранение ТС
        vehicle = None
        if carrier.vehicles:
            vehicle = carrier.vehicles[0]
        else:
            vehicle = Vehicle()
            carrier.vehicles.append(vehicle)
        
        vehicle.plate_number = self.vehicle_plate.text()
        vehicle.model = self.vehicle_model.text()
        try:
            vehicle.capacity = float(self.vehicle_capacity.text()) if self.vehicle_capacity.text() else 0.0
        except ValueError:
            vehicle.capacity = 0.0
        
        # Сохранение водителя
        driver = vehicle.driver
        if not driver:
            driver = Driver()
            vehicle.driver = driver
        
        driver.full_name = self.driver_name.text()
        driver.license_number = self.driver_license.text()
        driver.phone = self.driver_phone.text()
        
        session.commit()
        
        # Создание уведомления
        notification_manager = NotificationManager()
        notification_manager.create_notification(
            message=f"Перевозчик '{carrier.company_name}' {action}",
            notification_type="carrier",
            related_id=carrier.id
        )
        
        self.clear_fields()
        self.load_carriers()
    
    def delete_carrier(self):
        if self.current_id:
            reply = QMessageBox.question(
                self, 'Подтверждение удаления',
                'Вы уверены, что хотите удалить этого перевозчика?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                session = self.Session()
                carrier = session.query(Carrier).get(self.current_id)
                if carrier:
                    # Создание уведомления перед удалением
                    notification_manager = NotificationManager()
                    notification_manager.create_notification(
                        message=f"Перевозчик '{carrier.company_name}' удален",
                        notification_type="carrier",
                        related_id=carrier.id
                    )
                    
                    session.delete(carrier)
                    session.commit()
                    self.clear_fields()
                    self.load_carriers()
    
    def cancel_edit(self):
        self.clear_fields()
    
    def clear_fields(self):
        self.current_id = None
        self.id_label.setText("Новый перевозчик")
        self.company_input.clear()
        self.contact_input.clear()
        self.phone_input.clear()
        self.email_input.clear()
        self.vehicle_plate.clear()
        self.vehicle_model.clear()
        self.vehicle_capacity.clear()
        self.driver_name.clear()
        self.driver_license.clear()
        self.driver_phone.clear()
        self.delete_button.setEnabled(False)