
from PyQt5.QtWidgets import  QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette
from functools import partial

from system_functions import SystemHelpers, TimerHelper
from ui_helper import UserInterfaceHelper


class ValidationWindow(QWidget):
    """
    The class for handling user authentication through sending digits to the registered email
    and checking the digits to allow for resetting the password
    """

    def __init__(self, controller, login_page,  db, cursor):
        """
        Constructor for validation page
        """
        super().__init__()
        self.duration = 90
        self.time_left_int = self.duration
        self.timer = QTimer(self)
        self.system = SystemHelpers()
        self.controller = controller
        self.db = db
        self.cursor = cursor
        self.login_page = login_page
        self.user_interface()

    def user_interface(self):
        # set the size and name
        self.setWindowTitle('Reset Password')
        self.setFixedSize(400, 500)

        # set the color of the background 
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(UserInterfaceHelper.color_dic["validation_page"]['background_color']))
        self.setPalette(palette)

        # layout
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 70, 50, 70)
        layout.setSpacing(25)

        # Title
        title = QLabel('Reset Your Password')
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Arial', 20, QFont.Bold))
        title_color = title.palette()
        title_color.setColor(QPalette.WindowText, QColor(UserInterfaceHelper.color_dic["validation_page"]['title_color']))
        title.setPalette(title_color)

        # Login button
        submit_btn = QPushButton('Submit')
        submit_btn.setStyleSheet(UserInterfaceHelper.handle_button_style(True, UserInterfaceHelper.color_dic["validation_page"]['submit_button_color']['normal'],UserInterfaceHelper.color_dic["validation_page"]['submit_button_color']['focus'], underline_flag=False))
        submit_btn.setFont(QFont('Arial', 15, QFont.Bold))
        submit_btn.setFixedHeight(50)
        submit_btn.setCursor(Qt.PointingHandCursor)
        submit_btn.clicked.connect(self.handle_reset_password)

        self.timerLabel = QLabel("01:30", self)
        self.timerLabel.move(50, 50)
        self.timerLabel.setAlignment(Qt.AlignCenter)
        self.timerLabel.setStyleSheet("font: 17pt Helvetica;")

        # The blocks for random digits
        self.squares = []
        centering = Qt.AlignCenter
        square_layout = QHBoxLayout()

        for idx in range(6):
            square = QLineEdit()
            square.setMaxLength(1)
            square.setAlignment(centering)
            square.setObjectName("digit_box")

            square.textChanged.connect(partial(self.to_next_box, idx))
            square.keyPressEvent = partial(self.to_prev_box, idx)

            square_layout.addWidget(square)
            self.squares.append(square)

        layout.addWidget(title)
        layout.addLayout(square_layout)
        self.setLayout(layout)
        layout.addWidget(submit_btn)
        layout.addWidget(self.timerLabel)
        layout.addStretch()

        self.timer_manager = TimerHelper(label=self.timerLabel, timer=self.timer, duration=self.duration, expire_func=self.expire_func)

    def expire_func(self):
        """
        Activates when the random digit validity expires.
        Resend 6 digit random numbers to the registered email and
        clear the digits blocks
        """
        self.login_page.random_digits = self.system.send_reset_digits(
            6, username=self.login_page.username.text()
        )
        for square in self.squares:
            square.clear()

    def to_next_box(self, idx, _):
        """
        Moves to the next digit block when current is filled
        """
        if idx < 5:
            self.squares[idx + 1].setFocus()

    def to_prev_box(self, idx, input):
        """
        Moves back to the previous digit block when backspace is clicked
        """
        if input.key() == Qt.Key_Backspace:
            if not self.squares[idx].text() and idx > 0:
                self.squares[idx - 1].clear()
                self.squares[idx - 1].setFocus()

        QLineEdit.keyPressEvent(self.squares[idx], input)

    def handle_reset_password(self):
        """
        Activates when submit button is clicked.
        Checks the entered digits against the sent digits.
        If matched, stop the timer to prevent expiry function activating and shows password reset page.
        Else, shoe a warning message.
        """
        entered = "".join(i.text() for i in self.squares)
        if (self.login_page.random_digits == entered):
            self.timer.stop()
            self.controller.show_reset_password()
        else:
            QMessageBox.warning(
                self,
                'mismatch',
                'Codes dont not match"'
            )
            return

    def start_time(self):
        """
        Starts the timer
        """
        self.timer_manager.begin_timer()
