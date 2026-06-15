from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt, QTimer, pyqtSignal

from generated_files.change_confirmation_generated import Ui_change_confirmation
from system_functions import TimerHelper, SystemHelpers

class ChangeConfirmationPage(QDialog):
    finished = pyqtSignal() 
    """
    Email verification dialog used to confirm user identity before sensitive changes
    Sends a 6-digit code to the user's email and validates the entered code
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.userID = parent.userID
        self._parent = parent
        self.duration = 90
        self.timer = QTimer(self)
        self.system = SystemHelpers()
        self.code = self.system.send_reset_digits(6, userID=self.userID)

        self.ui = Ui_change_confirmation()
        self.ui.setupUi(self)

        self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint)
        self.change_information_signals_connection()
        self.change_information_show()

    def change_information_signals_connection(self):
        """
        Connects the submit and resend buttons and sets the initial timer label
        """
        self.ui.code_submit_button.clicked.connect(self.submit_code)
        self.ui.resend_button.clicked.connect(self.resend_button)
        self.ui.timer_label.setText("01:30")

    def change_information_show(self):
        """
        Sets up the countdown timer with an expiry function to resend the code
        """
        self.timer_manager = TimerHelper(self.ui.timer_label, self.timer, self.duration, expire_func=self.expire_func)

    def start_time(self):
        self.timer_manager.begin_timer()

    def expire_func(self):
        """
        Sends a new code when the timer expires and updates the stored code
        """
        code = self.system.send_reset_digits(
            6, userID=self.userID)
        self.code = code

    def resend_button(self):
        """
        Clears the input, resends the code, and restarts the timer
        """
        self.ui.confirmation_line.clear()
        self.expire_func()
        self.timer.stop()
        self.timer_manager.begin_timer()

    def submit_code(self):
        """
        Checks the entered code against the sent code
        Emits finished signal and closes the dialog if correct
        """
        entered_code =self.ui.confirmation_line.text()
        if entered_code == str(self.code):
            self.finished.emit()
            self.timer.stop()
            self.close()
        else:
            return

    def closeEvent(self, event):
        """
        Stops the timer when the dialog is closed
        """
        self.timer.stop()
        self.accept()
