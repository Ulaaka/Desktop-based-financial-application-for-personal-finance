import os, sys, certifi, django
from decouple import config

from PyQt5.QtWidgets import  QWidget, QMainWindow, QStackedWidget

from Widgets.login_page import LoginWindow
from Widgets.signup_page import SignUpWindow
from Widgets.validation_page import ValidationWindow
from Widgets.password_reset_page import PasswordResetWindow

from db_connection import Database
from Widgets.mainwindow import MainWindow

class UserAuthentication(QMainWindow):
    """
    Class for handling user authentication phase of the app which involves login, signup, reset password, and
    proceed to the main app page actions
    """
    def __init__(self):
        """
        Constructor for user authentication class
        """
        super().__init__()

        connection = Database()
        self.db = connection.db
        self.cursor = connection.cursor

        self.django_setup()

        self.setWindowTitle("Finance Reporter")
        self.setFixedSize(400, 500)


        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Creates the objects of the pages
        self.login_page = LoginWindow(self, self.db, self.cursor) 
        self.sign_up_page = SignUpWindow(self, self.db, self.cursor)

        self.validation_page = ValidationWindow(self, self.login_page, self.db, self.cursor)
        self.reset_password = PasswordResetWindow(self, self.login_page, self.db, self.cursor)
        self.dashboard_page = QWidget()

        # Add the pages to the stack
        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.sign_up_page)
        self.stacked_widget.addWidget(self.validation_page)
        self.stacked_widget.addWidget(self.reset_password)

    def show_dashboard(self, key, userID):
        """
        Proceeds to the main dashboard
        """
        self.main_window = MainWindow(self, key, userID)
        self.main_window.show()
        self.close()

    def show_login(self):
        """
        Proceeds to the login page
        """
        self.stacked_widget.setCurrentWidget(self.login_page)
        self.setMaximumSize(400, 500)

    def show_sign_up(self):
        """
        Proceeds to the signup page
        """
        self.stacked_widget.setCurrentWidget(self.sign_up_page)
        self.setMaximumSize(400, 500)

    def show_validation_page(self):
        """
        Proceeds to the validation page before resetting the password and
        starts the validation timer
        """
        self.stacked_widget.setCurrentWidget(self.validation_page)
        self.setMaximumSize(400, 500)
        self.validation_page.start_time()

    def show_reset_password(self):
        """
        Proceeds to the password resetting page
        """
        self.stacked_widget.setCurrentWidget(self.reset_password)
        self.setMaximumSize(400, 500)

    def django_setup(self):
        """
        Setting up django for authentication by email
        """
        sys.path.insert(0, config("CURRENT_FOLDER"))
        os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
        os.environ['SSL_CERT_FILE'] = certifi.where()
        os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
        django.setup()

    def start_login(self):
        self.login = UserAuthentication()
        self.login.show()
