from change_confirmation import Ui_change_confirmation
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt, QTimer
from queries import query_processor
from ui_support_functions import ui_support_functions
from system_functions import manage_seconds_qt, system_functions


class Change_confirmation_page(QDialog):
    def __init__(self, code, parent):
        super().__init__(parent)
        self.userID = parent.userID
        self.code = code
        self.system = system_functions()
        self.timer = QTimer(self)
        self.duration = 90

        self.ui = Ui_change_confirmation()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.Popup)
        self.change_information_signals_connection()
        self.change_information_show()

    def change_information_signals_connection(self):
        self.ui.code_submit_button.clicked.connect(self.submit_code)
        self.ui.resend_button.clicked.connect(self.resend_code)

    def change_information_show(self):
        timer_label = self.ui.timer_label
        self.timer_manager = manage_seconds_qt(timer_label, self.timer, self.duration, expire_func=self.expire_func)

    def start_time(self):
        self.timer_manager.begin_timer()

    def expire_func(self):
        self.code = self.system.send_reset_digits(
            6, userID=self.userID)

    def submit_code(self):
        pass

    def resend_code(self):
        # needs to update the code
        pass
