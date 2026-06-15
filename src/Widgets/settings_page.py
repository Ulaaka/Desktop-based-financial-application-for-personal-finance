import os, base64, secrets

from PyQt5.QtWidgets import QMessageBox, QLineEdit, QPushButton, QHeaderView
from PyQt5.QtCore import QPoint, QSortFilterProxyModel, Qt

from Widgets.change_confirmation_window import ChangeConfirmationPage
from Widgets.app_table_helper import CategoryTable
from Widgets.home_page import HomePage

from db_queries import QueryProcessor
from base_classes import PasswordHelper, CryptoHelper
from system_functions import SystemHelpers

class Change_password_page():
    """
    Class for handling the password change from the main app
    """
    def __init__(self, parent):
        self._parent = parent
        self.password_manager = PasswordHelper()
        self.query = QueryProcessor()
        self.objective = 0
        self.change_password_signals_connect()

    def change_password_signals_connect(self):
        """
        Connect the widget signals
        """
        parent_window = self._parent
        parent_window.ui.change_password_button_settings.clicked.connect(self.change_password)
        parent_window.ui.forgot_password_button_settings.clicked.connect(self.forgot_password_handle)
        parent_window.ui.current_password_line.setEchoMode(QLineEdit.Password)
        parent_window.ui.new_password_line.setEchoMode(QLineEdit.Password)
        parent_window.ui.new_password_line.setToolTip(
            "Your password must be at least 8 characters \n"
            "should include: \n"
            "- a combination of numbers\n"
            "- letters\n"
            "- special characters (!$@%)"
        )

    def change_password(self):
        """
        Handles password change for both standard and forgot password flows.
        For standard change, validates the current password before updating.
        For forgot password, decrypts the data key via RSA and re-encrypts with the new password.
        """

        crypto = CryptoHelper()
        system = SystemHelpers()
        query = QueryProcessor()
        parent_window = self._parent
        current_password = parent_window.ui.current_password_line.text()
        new_password = parent_window.ui.new_password_line.text()
        if (self.objective == 0):
            # standard password change 
            safety = self.password_manager.check_password_safety(new_password)

            if current_password and new_password:
                if not safety:
                    QMessageBox.warning(
                        parent_window,
                        'Error',
                        "Your password must be at least 8 characters\n"
                        "should include:\n"
                        "- a combination of numbers\n"
                        "- letters\n"
                        "- special characters (!$@%)"
                    )
                    return

                hash_password = self.query.get_hashed_password(userID=parent_window.userID)[0]
                compare_current = self.password_manager.check_password(current_password, hash_password)

                if not compare_current:
                    QMessageBox.warning(
                        parent_window, 'Error', "Current Password Does Not Match")
                    return

                compare_new = self.password_manager.check_password(new_password, hash_password)

                if compare_new:
                    QMessageBox.warning(
                        parent_window, 'Error', "New password must different from current password")
                    return

                result = self.password_manager.change_password(parent_window.userID, new_password)
                # password changed
                if result:
                    parent_window.ui.current_password_line.clear()
                    parent_window.ui.new_password_line.clear()
                    # re-encrypt data key with new password
                    enc_data_key, salt = system.update_data_key(current_password, new_password, self._parent.userID)
                    query.update_key_salt(enc_data_key, salt, self._parent.userID)
                    QMessageBox.information(
                        parent_window, "Confirmation", "Password Changed")
                    return
            else:
                QMessageBox.warning(
                    parent_window, "Error", "Please enter both fields")
                return
        else:
            # when forgot password
            result = self.password_manager.change_password(parent_window.userID, new_password)
            if result:
                parent_window.ui.current_password_line.show()
                parent_window.ui.current_password_line.clear()
                parent_window.ui.new_password_line.clear()
                self.objective = 0

                new_salt = os.urandom(32)
                new_wrapping_key = crypto.generate_key(new_password, new_salt)

                _, _, encrypted_data_key_server = self.query.get_data_key_salt(parent_window.userID)
                _, private_key = crypto.retrieve_keys_pem()
                data_key = crypto.decrypt_rsa(encrypted_data_key_server, private_key)

                new_encrypted_data_key = crypto.encrypt_data_key(new_wrapping_key, data_key)
                query.update_key_salt(new_encrypted_data_key, new_salt, parent_window.userID)
                QMessageBox.information(
                    parent_window, "Confirmation", "Password Changed")
                return

    def forgot_password_handle(self):
        """
        Opens the email verification window the forgot password button is clicked.
        """

        parent_window = self._parent
        confirmation_window = ChangeConfirmationPage(parent_window)
        confirmation_window.finished.connect(self.capture_result)
        global_pos = parent_window.ui.forgot_password_button_settings.mapToGlobal(QPoint(0,0))
        confirmation_window.move(global_pos.x(), global_pos.y() + parent_window.ui.forgot_password_button_settings.height())
        confirmation_window.start_time()
        confirmation_window.show()

    def capture_result(self):
        """
        Called after email verification succeeds, hides the current password
        field and switches to the forgot password mode.
        """
        parent_window = self._parent
        parent_window.ui.current_password_line.hide()
        parent_window.ui.new_password_line.clear()
        self.objective = 1

class Delete_user_account():
    """
    Handles  deletion of the user account after password verification.
    """

    def __init__(self, parent):
        self._parent = parent
        self.query = QueryProcessor()
        self.password_manager = PasswordHelper()
        self.delete_user_signals_connect()

    def delete_user_signals_connect(self):
        """
        Connects delete account widget signals to their handler methods.
        """

        parent_window = self._parent
        parent_window.ui.delete_user_button_2.clicked.connect(self.delete_user)
        parent_window.ui.delete_user_line.setEchoMode(QLineEdit.Password)

    def delete_user(self):
        """
        Verifies the entered password and deletes the user account if it matches.
        Logs the user out before deletion.
        """

        parent_window = self._parent
        current_password = self._parent.ui.delete_user_line.text()

        # this needs to be a single func
        hash_password = self.query.get_hashed_password(userID=parent_window.userID)[0]
        compare = self.password_manager.check_password(current_password, hash_password)
        if compare:
            parent_window.log_out()
            self.query.delete_user(parent_window.userID)

class Change_category():
    """
    Handles the category management page, including displaying, adding,
    removing, and searching categories.
    """
    def __init__(self, parent):
        self._parent = parent
        self.home_page = HomePage(parent)
        self.category_signals_connect()

    def category_signals_connect(self):
        """
        Signals are connected
        """
        parent_window = self._parent
        parent_window.ui.category_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        parent_window.ui.category_table.verticalHeader().setVisible(False)

    def show_category_table(self):
        """
        Retrieves categories for the selected account and loads them into
        the category table with search and sort proxy support.
        An empty row is appended at the bottom to allow new category creation.
        """

        query = QueryProcessor()
        parent_window = self._parent
        if not parent_window.accountID:
            QMessageBox.warning(parent_window, "error", "Please create an account first")
            return

        categories = query.get_category_info(parent_window.userID, parent_window.accountID, asDF=True)
        # add extra row to allow for category add
        categories.loc[len(categories)] = [-1, "", "", ""]
        self.set_category_table(True)

        # -- TABLE LOADING -- 
        self.model = CategoryTable(categories, parent_window, self)
        self.data = categories

        # Set the search filter for the table
        # inspired from:  https://www.youtube.com/watch?v=53bZSTSLUqI

        proxy_model = QSortFilterProxyModel()
        proxy_model.setSourceModel(self.model)
        proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        proxy_model.setFilterKeyColumn(2)
        parent_window.ui.category_line.textChanged.connect(lambda text: self.filtered_search(text, proxy_model, categories))
        parent_window.ui.category_table.setModel(proxy_model)

        self.load_buttons(proxy_model, categories)
        # hide the id, list columns
        hidden_columns = [0, 1]
        for i in hidden_columns:
            parent_window.ui.category_table.setColumnHidden(i, True)


    def set_category_table(self, flag):
        """
        Switches between the category table page and the empty state page.
        :param flag: True to show the table, False to show the empty state
        """

        parent_window = self._parent
        if flag:
            parent_window.ui.settings_stack.setCurrentWidget(parent_window.ui.category_table_page)
        else:
            parent_window.ui.settings_stack.setCurrentWidget(parent_window.ui.no_category_page)


    def handle_add_button(self):

        """
        Adds a new category using the name and description entered in the table,
        then refreshes both the category and transaction tables.
        """

        query = QueryProcessor()
        parent_window = self._parent
        description = self.model.description
        name = self.model.name

        query.add_category_update(parent_window.userID, parent_window.accountID, description, name)
        self.show_category_table()
        self.home_page.show_table()

    def handle_remove_button(self, categoryID, category_name):

        """
        Deletes the selected category and reassigns affected transactions,
        then refreshes both the category and transaction tables.
        :param categoryID: ID of the category to delete
        :param category_name: name of the category to delete
        """

        parent_window = self._parent
        query = QueryProcessor()
        query.delete_category(int(categoryID))
        query.update_transaction_after_deletion(parent_window.userID, parent_window.accountID, str(category_name))
        self.show_category_table()
        self.home_page.show_table()

    def filtered_search(self, text, proxy, categories):
        """
        Applies a search filter to the category table and reloads row buttons.
        :param text: search string entered by the user
        :param proxy: proxy model managing the filtered view
        :param categories: full categories dataframe for button mapping
        """
        proxy.setFilterRegExp(text)
        self.load_buttons(proxy, categories)

    def load_buttons(self, proxy, categories):
        """
        Inserts an add button on the last row and remove buttons on all other rows.
        :param proxy: proxy model used to map rows to source indices
        :param categories: full categories dataframe for button mapping
        """

        parent_window = self._parent
        for row_index in range(proxy.rowCount()):
            index_button = proxy.index(row_index, proxy.columnCount() - 1)
            source_model = proxy.sourceModel()
            source_index = proxy.mapToSource(index_button)
            category_id = source_model._data.iloc[source_index.row(), 0]
            category_name = source_model._data.iloc[source_index.row(), 3]
            if (proxy.rowCount() == 1 or row_index >= proxy.rowCount() - 1):
                add_button = QPushButton("Add")
                add_button.setObjectName("view_button")
                parent_window.ui.category_table.setIndexWidget(index_button, add_button)
                add_button.clicked.connect(lambda : self.handle_add_button())
            else:
                remove_button = QPushButton("Remove")
                remove_button.setObjectName("item_button")
                parent_window.ui.category_table.setIndexWidget(index_button, remove_button)
                remove_button.clicked.connect(lambda clicked, id=category_id, name = category_name: self.handle_remove_button(id, name))