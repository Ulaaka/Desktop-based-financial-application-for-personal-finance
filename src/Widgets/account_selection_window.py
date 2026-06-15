from PyQt5.QtWidgets import QDialog, QCompleter
from PyQt5.QtCore import Qt,pyqtSignal

from generated_files.account_selection_generated import Ui_AccountSelection
from Widgets.account_add_window import AccountAddPage
from db_queries import QueryProcessor

class AccountSelectionWindow(QDialog):
    """
    Popup dialog for selecting or adding an account
    """
    chose_account = pyqtSignal(str, int)
    def __init__(self, parent):
        super().__init__(parent)

        self._parent = parent
        self.userID = parent.userID
        self.currency_list = parent.currency_list

        self.ui = Ui_AccountSelection()

        self.ui.setupUi(self)
        self.setWindowFlags(Qt.Popup)

        self.set_completer(self.ui.lineEdit, self.ui.accounts_list.model())
        self.account_selection_signals_connection()
        self.show_accounts()

    def account_selection_signals_connection(self):
        """
        Connects account list changes and add account buttons to their handlers
        """
        self.ui.accounts_list.model().rowsInserted.connect(self.update_list)
        self.ui.accounts_list.model().rowsRemoved.connect(self.update_list)
        self.ui.add_accounts_empty.clicked.connect(self.add_accounts)
        self.ui.add_accounts_list.clicked.connect(self.add_accounts)

    def show_accounts(self):
        """
        Fetches and displays all accounts for the current user
        Connects selection changes to set_account
        """
        query = QueryProcessor()
        self.ui.accounts_list.clear()
        self.account_options = query.compute_account_options(self.userID)
        if self.account_options:
            self.ui.accounts_list.addItems(self.account_options)
            self.ui.accounts_list.currentTextChanged.connect(self.set_account)
        self.update_list()

    def set_account(self, option):
        """
        Emits the selected account name and ID to the main window
        :param option: the selected account name
        """
        query = QueryProcessor()
        accountID = query.get_accountID(option, self.userID)
        self.chose_account.emit(option, accountID)

    def set_completer(self, search, model):
        """
        connects a case-insensitive search completer to the search field
        :param search: the search line edit widget
        :param model: the list model to search through
        """
        self.completer = QCompleter(model, search)
        self.completer.setFilterMode(Qt.MatchContains)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        search.setCompleter(self.completer)

    def update_list(self):
        """
        Toggles between the accounts list view and the empty state view
        Also resizes the dialog to fit its contents
        """
        if (self.ui.accounts_list.count() > 0):
            self.ui.accounts_list.setVisible(True)
            self.ui.add_accounts_list.setVisible(True)
            self.ui.empty_container.setVisible(False)
        else:
            self.ui.accounts_list.setVisible(False)
            self.ui.add_accounts_list.setVisible(False)
            self.ui.empty_container.setVisible(True)
        self.adjustSize()

    def add_accounts(self):
        """
        Opens the add account window
        """
        self.account_add_page = AccountAddPage(self.currency_list, self)
        self.account_add_page.show()