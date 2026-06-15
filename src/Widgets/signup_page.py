import os, secrets,  base64
from decouple import config

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPalette

from base_classes import PasswordHelper, CryptoHelper
from db_queries import QueryProcessor
from ui_helper import UserInterfaceHelper


class SignUpWindow(QWidget):
    """
    Class for handling signup page
    """

    def __init__(self, controller, db, cursor):
        super().__init__()
        self.controller = controller
        self.db = db
        self.cursor = cursor
        self.user_interface()
        self.query = QueryProcessor()

    def user_interface(self):
        """
        Setup the user interface widgets
        """
        # set the size and name
        self.setWindowTitle('Sign Up')
        self.setFixedSize(400, 500)
        # set the color of the background
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(UserInterfaceHelper.color_dic["sign_up_page"]["background_color"]))
        self.setPalette(palette)

        # layout
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 70, 50, 70)
        layout.setSpacing(25)

        # Title
        title = QLabel('Create a new account')
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Arial', 20, QFont.Bold))
        title_color = title.palette()
        title_color.setColor(QPalette.WindowText, QColor(UserInterfaceHelper.color_dic["sign_up_page"]['title_color']))
        title.setPalette(title_color)

        # Username input
        self.username = QLineEdit()
        self.username.setPlaceholderText('Username')
        self.username.setObjectName("input_field")
        self.username.setFont(QFont('Arial', 15))

        # Password input
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText('Password')
        self.password.setObjectName("input_field")
        self.password.setFont(QFont('Arial', 15))
        self.password.setToolTip(
            "Your password must be at least 8 characters \n"
            "should include: \n"
            "- a combination of numbers\n"
            "- letters\n"
            "- special characters (!$@%)"
        )

        # email input
        self.email = QLineEdit()
        self.email.setPlaceholderText('Email')
        self.email.setObjectName("input_field")
        self.email.setFont(QFont('Arial', 15))

        # Login button
        submit_btn = QPushButton('Submit')
        submit_btn.setStyleSheet(UserInterfaceHelper.handle_button_style(True, UserInterfaceHelper.color_dic["sign_up_page"]["submit_button_color"]["normal"], UserInterfaceHelper.color_dic["sign_up_page"]["submit_button_color"]["focus"], underline_flag=False))
        submit_btn.setFont(QFont('Arial', 15, QFont.Bold))
        submit_btn.setFixedHeight(50)
        submit_btn.setCursor(Qt.PointingHandCursor)
        submit_btn.clicked.connect(self.handle_submit)

        # already have an account?
        got_account = QPushButton('Already have an account?')
        got_account.setStyleSheet(UserInterfaceHelper.handle_button_style(False, "transparent", 'green',  underline_flag=True))
        got_account.setCursor(Qt.PointingHandCursor)
        got_account.clicked.connect(self.handle_got_account)

        # Add widgets to layout
        layout.addWidget(title)
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(self.email)
        layout.addWidget(submit_btn)
        layout.addWidget(got_account, alignment=Qt.AlignCenter)
        layout.addStretch()
        self.setLayout(layout)

    def handle_got_account(self):
        """
        Navigates to login page when the user already have an account
        """
        self.controller.show_login()
        pass

    def handle_submit(self):
        """
        Handles the scenario when the new user information is submitted
        - Validates the information fields
        - Creates unique keys for the user to allow for cryptography
        - Inserts the user infos after securing safety
        - Navigates to the login page
        """
        username_local = self.username.text()
        password_local = self.password.text()
        email_local = self.email.text()

        password_manager = PasswordHelper()

        result = self.query.get_userID(username_local)

        # Validates the information fields
        if not username_local or not password_local or not email_local:
            QMessageBox.warning(self, 'Error', 'Please enter all  the credentials, thank you')
            return

        if result:
            QMessageBox.warning(self, 'Error', 'Username already exists, please try another username')
            return

        if not password_manager.check_password_safety(password_local):
            QMessageBox.warning(self, 'Not Satisfied', 'Password Requirement not satisfied')
            return

        if not password_manager.check_email_validity(email_local):
            QMessageBox.warning(self, 'Invalid', 'Invalid email')
            return

        # Generate the random salt for wrapping key creation
        crypto = CryptoHelper()
        salt = os.urandom(32)

        # Create the wrapping key using password and salt combination
        wrapping_key = crypto.generate_key(password_local, salt)

        # Generate unique data key for the user upon creation
        data_key = base64.urlsafe_b64encode(secrets.token_bytes(32))

        # Encrypt the data key with the wrapping key
        encrypted_data_key = crypto.encrypt_data_key(wrapping_key, data_key)

        # If it is the first user, generate RSA public and private key
        # It allows for recovery when the user forgets the password instead of deleting all the user data
        if not os.path.exists(config("PEM_FOLDER")):
            public_key, private_key = crypto.generate_pub_priv_keys()
            crypto.generate_save_to_pems(public_key, private_key)
        else:
            # Retrieve the existing public key for recovery encrypted data key
            public_key, _ = crypto.retrieve_keys_pem()

        enc_data_key_public = crypto.encrypt_rsa(data_key, public_key)

        # Hash the password
        hashed_password = password_manager.hash_password(password_local)
        self.query.insert_user(username_local, hashed_password, email_local, encrypted_data_key, enc_data_key_public, salt)
        self.controller.show_login()