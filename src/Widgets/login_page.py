
from PyQt5.QtWidgets import  QWidget,QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPalette

from base_classes import PasswordHelper, CryptoHelper
from system_functions import SystemHelpers
from db_queries import QueryProcessor
from ui_helper import UserInterfaceHelper

class LoginWindow(QWidget):
    """
    Handles the login window - allows the user to log in, sign up, or reset their password
    """
    def __init__(self, controller, db, cursor):
        super().__init__()
        self.controller = controller
        self.db = db
        self.cursor = cursor
        self.system = SystemHelpers()
        self.query = QueryProcessor()

        self.user_interface()

    def user_interface(self):
        """
        Builds the login window layout with username, password fields and action buttons
        """
        # set the size and name
        self.setWindowTitle('Finance Login')
        self.setFixedSize(400, 500)

        # set the color of the background
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(UserInterfaceHelper.color_dic["login_page"]["background_color"]))
        self.setPalette(palette)

        # layout
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 70, 50, 70)
        layout.setSpacing(25)

        # Title
        title = QLabel('Finance Reporter')
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Arial', 20, QFont.Bold))
        title_color = title.palette()
        title_color.setColor(QPalette.WindowText, QColor(UserInterfaceHelper.color_dic["login_page"]["title_color"]))
        title.setPalette(title_color)

        # Username input
        self.username = QLineEdit()
        self.username.setPlaceholderText('Username')
        self.username.setObjectName("input_field")
        self.username.setFont(QFont('Arial', 15))


        # Password input
        self.password = QLineEdit()
        self.password.setPlaceholderText('Password')

        # hiding the password
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setObjectName("input_field")
        self.password.setFont(QFont('Arial', 15))

        # Login button
        login_btn = QPushButton('Log In')
        login_btn.setStyleSheet(UserInterfaceHelper.handle_button_style(True, UserInterfaceHelper.color_dic["login_page"]['login_button_color']["normal"], UserInterfaceHelper.color_dic["login_page"]['login_button_color']["focus"], underline_flag=False))
        login_btn.setFont(QFont('Arial', 15, QFont.Bold))
        login_btn.setFixedHeight(50)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.clicked.connect(self.handle_login)

        # sign up button
        signup_btn = QPushButton('Create new account')
        signup_btn.setStyleSheet(UserInterfaceHelper.handle_button_style(True, UserInterfaceHelper.color_dic["login_page"]["sign_up_button_color"]["normal"], UserInterfaceHelper.color_dic["login_page"]["sign_up_button_color"]["focus"], underline_flag=False))
        signup_btn.setFont(QFont('Arial', 15, QFont.Bold))
        signup_btn.setFixedHeight(50)
        signup_btn.setCursor(Qt.PointingHandCursor)
        signup_btn.clicked.connect(self.handle_sign_up)

        # Forgot password link
        forgot_password = QPushButton('Forgotten password?')
        forgot_password.setStyleSheet(UserInterfaceHelper.handle_button_style(False, "transparent", "green",  underline_flag=True))
        forgot_password.setCursor(Qt.PointingHandCursor)
        forgot_password.clicked.connect(self.handle_forgot_password)

        # Add widgets to layout
        layout.addWidget(title)
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(login_btn)
        layout.addWidget(forgot_password, alignment=Qt.AlignCenter)
        layout.addWidget(signup_btn)
        layout.addStretch()
        self.setLayout(layout)

    def handle_sign_up(self):
        """
        Navigates to the sign up window
        """
        self.controller.show_sign_up()

    def handle_login(self):
        """
        Validates credentials, decrypts the data key on success, and opens the dashboard
        """
        username_local = self.username.text()
        password_local = self.password.text()
        query = QueryProcessor()
        password_manager = PasswordHelper()
        crypto = CryptoHelper()

        if not username_local or not password_local:
            QMessageBox.warning(self, 'Error', 'Please enter both of the credentials, thank you')
            return

        result = query.get_hashed_password(username=username_local)

        if result and password_manager.check_password(password_local, result[0]):
                userID = query.get_userID(username_local)
                enc_data_key, salt, _ = query.get_data_key_salt(userID)
                wrapping_key = crypto.generate_key(password_local, salt)
                data_key = crypto.decrypt_data_key(wrapping_key, enc_data_key)
                self.controller.show_dashboard(data_key, userID)
        else:
            QMessageBox.warning(self, 'Error', 'Password or Username is wrong')
            return

    def handle_forgot_password(self):
        """
        Sends a reset code to the user's email and navigates to the validation page
        Username must be entered before clicking this
        """
        username_local = self.username.text()

        if not username_local:
            QMessageBox.information(
                self,
                'Forgot Password',
                'Please enter your username first, then click "Forgot your password?"'
            )
            return

        self.random_digits = self.system.send_reset_digits(6, username=username_local)
        if self.random_digits:
            self.controller.show_validation_page()
        else:
            QMessageBox.warning(self, 'Error', 'The user Does Not Exist')
            return
