from PyQt6.QtWidgets import QMainWindow, QTabWidget, QStatusBar, QToolBar
from PyQt6.QtGui import QAction
from .client_form import ClientForm
from .carrier_form import CarrierForm
from .order_form import OrderForm
from .payment_form import PaymentForm
from .document_form import DocumentForm
from .report_form import ReportForm
from .notification_widget import NotificationWidget
from PyQt6.QtCore import QTimer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MurphyLogistik")
        self.setGeometry(100, 100, 1200, 800)
        
        # Создаем вкладки
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Вкладка клиентов
        self.client_tab = ClientForm()
        self.tabs.addTab(self.client_tab, "Клиенты")
        
        # Вкладка перевозчиков
        self.carrier_tab = CarrierForm()
        self.tabs.addTab(self.carrier_tab, "Перевозчики")
        
        # Вкладка заказов
        self.order_tab = OrderForm()
        self.tabs.addTab(self.order_tab, "Заказы")
        
        # Вкладка платежей
        self.payment_tab = PaymentForm()
        self.tabs.addTab(self.payment_tab, "Платежи")
        
        # Вкладка документов
        self.document_tab = DocumentForm()
        self.tabs.addTab(self.document_tab, "Документы")
        
        # Вкладка отчетов
        self.report_tab = ReportForm()
        self.tabs.addTab(self.report_tab, "Отчеты")
        
        # Панель инструментов
        self.toolbar = QToolBar("Панель инструментов")
        self.addToolBar(self.toolbar)
        
        # Кнопка уведомлений
        self.notification_action = QAction("Уведомления", self)
        self.notification_action.triggered.connect(self.show_notifications)
        self.toolbar.addAction(self.notification_action)
        
        # Статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Виджет уведомлений
        self.notification_widget = NotificationWidget()
        
        # Таймер для проверки новых уведомлений
        self.notification_timer = QTimer()
        self.notification_timer.timeout.connect(self.check_notifications)
        self.notification_timer.start(30000)  # Проверка каждые 30 секунд
        self.check_notifications()  # Первоначальная проверка
    
    def show_notifications(self):
        self.notification_widget.show()
        self.notification_widget.activateWindow()
        self.notification_widget.load_notifications()
    
    def check_notifications(self):
        unread_count = self.notification_widget.notification_manager.get_unread_count()
        if unread_count > 0:
            self.notification_action.setText(f"Уведомления ({unread_count})")
            self.status_bar.showMessage(f"У вас {unread_count} непрочитанных уведомлений")
        else:
            self.notification_action.setText("Уведомления")
            self.status_bar.clearMessage()