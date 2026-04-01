from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QPushButton
class TurnListButton(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def addItem(self, options_list):
        for option in options_list:
            account = QListWidgetItem()
            account_button = QPushButton(option)

            account_button.clicked.connect(lambda checked, option=option: self.button_clicked.emit(option))
            super().addItem(account)
            self.setItemWidget(account, account_button)
            account.setSizeHint(account_button.sizeHint())