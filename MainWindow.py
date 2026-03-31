import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QListWidget, QWidget
from PyQt5.QtCore import Qt, QPoint

from financial_app import Ui_MainWindow
from account_selection_panel import Ui_Form
from queries import query_processor
class account_selection(QWidget):
    def __init__(self, account_options):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.account_list.addItems(account_options)
        self.setWindowFlags(Qt.Popup)

class MainWindow(QMainWindow):
    def __init__(self, controller , key, userID):
        super(MainWindow, self).__init__()

        self.controller = controller
        self.key = key
        self.userID = userID

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.full_menu_widget.hide()
        self.ui.stackedWidget.setCurrentIndex(0)
        self.buttons_connected()

        self.query = query_processor()
        accounts = self.query.return_accounts_given_userID(self.userID)
        accounts_list = [account[1] for account in accounts]
        self.accounts_selection_panel = account_selection(self, accounts_list)
        self.accounts_selection_panel.hide()

    def buttons_connected(self):
        self.ui.home_button_1.clicked.connect(self.home_page_show)
        self.ui.home_button_2.clicked.connect(self.home_page_show)

        self.ui.upload_button_1.clicked.connect(self.upload_page_show)
        self.ui.upload_button_2.clicked.connect(self.upload_page_show)

        self.ui.file_button_1.clicked.connect(self.file_page_show)
        self.ui.file_button_2.clicked.connect(self.file_page_show)

        self.ui.stats_button_1.clicked.connect(self.stats_page_show)
        self.ui.stats_button_2.clicked.connect(self.stats_page_show)

        self.ui.profile_button_1.clicked.connect(self.profile_page_show)
        self.ui.profile_button_2.clicked.connect(self.profile_page_show)

        self.ui.settings_button_1.clicked.connect(self.settings_page_show)
        self.ui.settings_button_2.clicked.connect(self.settings_page_show)

        self.ui.account_button.clicked.connect(self.accounts_selection_show)


    def home_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.home_page)

    def upload_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.upload_page)

    def file_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.files_page)

    def stats_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.stats_page)

    def profile_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.profile_page)

    def settings_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.settings_page)

    # needs to be polished
    def accounts_selection_show(self):
        button = self.ui.account_button
        pos = button.mapToGlobal(QPoint(0, button.height()))
        self.accounts_panel.move(pos)
        self.accounts_panel.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    with open('style.qss', 'r') as styling:
        style = styling.read()

    app.setStyleSheet(style)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())
