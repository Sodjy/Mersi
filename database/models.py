from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Boolean, Text, DateTime
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Client(Base):
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    contact_person = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(String(200))
    orders = relationship("Order", back_populates="client")
    is_active = Column(Boolean, default=True)

class Carrier(Base):
    __tablename__ = 'carriers'
    id = Column(Integer, primary_key=True)
    company_name = Column(String(100), nullable=False)
    contact_person = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    vehicles = relationship("Vehicle", back_populates="carrier")
    is_active = Column(Boolean, default=True)

class Vehicle(Base):
    __tablename__ = 'vehicles'
    id = Column(Integer, primary_key=True)
    plate_number = Column(String(20), nullable=False)
    model = Column(String(50))
    capacity = Column(Float)
    carrier_id = Column(Integer, ForeignKey('carriers.id'))
    carrier = relationship("Carrier", back_populates="vehicles")
    driver = relationship("Driver", uselist=False, back_populates="vehicle")

class Driver(Base):
    __tablename__ = 'drivers'
    id = Column(Integer, primary_key=True)
    full_name = Column(String(100), nullable=False)
    license_number = Column(String(50))
    phone = Column(String(20))
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'))
    vehicle = relationship("Vehicle", back_populates="driver")

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'))
    carrier_id = Column(Integer, ForeignKey('carriers.id'))
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'))
    loading_address = Column(String(200), nullable=False)
    unloading_address = Column(String(200), nullable=False)
    cargo_name = Column(String(100))
    packaging = Column(String(50))
    weight = Column(Float)
    loading_type = Column(String(50))
    order_date = Column(Date)
    loading_date = Column(Date)
    status = Column(String(20), default='Создан')
    documents = relationship("Document", back_populates="order")
    
    client = relationship("Client", back_populates="orders")
    carrier = relationship("Carrier")
    vehicle = relationship("Vehicle")
    payments = relationship("Payment", back_populates="order")

class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    amount = Column(Float, nullable=False)
    payment_date = Column(Date)
    is_client_payment = Column(Boolean)  # True - от клиента, False - перевозчику
    description = Column(String)
    order = relationship("Order", back_populates="payments")

class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    name = Column(String(100))
    file_path = Column(String(200))
    description = Column(Text)
    order = relationship("Order", back_populates="documents")

class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, default=0)  # ID пользователя
    message = Column(String(255), nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    related_id = Column(Integer)  # ID связанного объекта (заказ, платеж и т.д.)
    notification_type = Column(String(50))  # Тип уведомления: order, payment, document