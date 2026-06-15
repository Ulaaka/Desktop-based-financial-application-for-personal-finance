from PyQt5.QtWidgets import QDialog, QCompleter, QMessageBox
from PyQt5.QtCore import Qt

from generated_files.account_add_generated import Ui_AccountAdd
from db_queries import QueryProcessor

class AccountAddPage(QDialog):
    """
    Dialog for adding a new account with a name, type, and currency
    """
    def __init__(self, currencies, parent):
        super().__init__(parent)
        self.userID = parent.userID
        self.currencies = currencies

        self.ui = Ui_AccountAdd()

        self.ui.setupUi(self)
        self.account_add_signals_connection()

    def account_add_signals_connection(self):
        """
        Populates the currency dropdown, attaches a search completer, and connects the submit button
        """
        self.ui.currency_select_combo.addItems(self.currencies)
        self.ui.submit_button.clicked.connect(self.add_account_database)
        currency_search = self.ui.currency_select_combo.lineEdit()
        currency_search.setPlaceholderText("Search currency...")
        completer = QCompleter(self.ui.currency_select_combo.model(), self)

        completer.setFilterMode(Qt.MatchContains)
        completer.setCaseSensitivity(Qt.CaseInsensitive)

    def add_account_database(self):
        """
        Reads the entered account details and inserts the new account into the database
        Updates the main window to reflect the newly added account
        Shows a warning if any field is missing
        """
        query = QueryProcessor()
        account_name = self.ui.name_select_combo.text()
        account_type = self.ui.type_select_combo.currentText()
        account_currency = self.ui.currency_select_combo.currentText()[:3]
        if account_name and account_type and account_currency:
            accountID = query.insert_account(self.userID, account_name, account_type, account_currency)

            self.parent().parent().update_account(account_name, accountID)
            self.parent().parent().update_current_widget()
            self.close()
        else:
            self.close()
            QMessageBox.warning(self.parent().parent(), 'Error', 'Please enter all information')
            return