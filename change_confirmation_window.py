from change_confirmation import Ui_change_confirmation
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt, QTimer
from queries import query_processor
from ui_support_functions import ui_support_functions
from system_functions import manage_seconds_qt


class Change_confirmation_page(QDialog):
    def __init__(self, code, parent):
        super().__init__(parent)
        self.userID = parent.userID
        self.code = code
        self.query = query_processor()
        self.timer = QTimer(self)
        self.duration = 90

        self.ui = Ui_change_confirmation()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.Popup)

    def change_information_signals_connection(self):
        self.ui.code_submit_button.clicked.connect(self.submit_code)
        self.ui.resend_button.clicked.connect(self.resend_code)

    def change_information_show(self):
        timer_label = self.ui.timer_label
        self.timer_manager = manage_seconds_qt(timer_label, self.timer, self.duration)

    def start_time(self):
        self.timer_manager.begin_timer()

    def submit_code(self):
        pass

    def resend_code(self):
        # needs to update the code
        pass
