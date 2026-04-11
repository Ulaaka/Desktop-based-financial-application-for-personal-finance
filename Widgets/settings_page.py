from PyQt5.QtWidgets import QMessageBox, QLineEdit, QPushButton, QHeaderView
from PyQt5.QtCore import QPoint, QSortFilterProxyModel, Qt

from queries import query_processor
from BASE_Classes import password_class
from Widgets.change_confirmation_window import Change_confirmation_page
from Widgets.Table_View import ListModelCategory
from Widgets.home_page import Home_page
import numpy as np
class Change_password_page():
    def __init__(self, parent):
        self._parent = parent
        self.password_manager = password_class()
        self.query = query_processor()
        self.objective = 0
        self.change_password_signals_connect()
    
    def change_password_signals_connect(self):
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
        parent_window = self._parent
        current_password = parent_window.ui.current_password_line.text()
        new_password = parent_window.ui.new_password_line.text()
        if (self.objective == 0):
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
                compare = self.password_manager.check_password(current_password, hash_password)
                if not compare:
                    QMessageBox.warning(
                        parent_window, 'Error', "Current Password Does Not Match")
                    return

                result = self.password_manager.change_password(parent_window.userID, new_password)
                if result:
                    parent_window.ui.current_password_line.clear()
                    parent_window.ui.new_password_line.clear()
                    QMessageBox.information(
                        parent_window, "Confirmation", "Password Changed")
                    return
            else:
                QMessageBox.warning(
                    parent_window, "Error", "Please enter both fields")
                return
        else:
            result = self.password_manager.change_password(parent_window.userID, new_password)
            if result:
                parent_window.ui.current_password_line.show()
                parent_window.ui.current_password_line.clear()
                parent_window.ui.new_password_line.clear()
                self.objective = 0
                QMessageBox.information(
                    parent_window, "Confirmation", "Password Changed")
                return

    def forgot_password_handle(self):
        parent_window = self._parent
        confirmation_window = Change_confirmation_page(parent_window)
        confirmation_window.finished.connect(self.capture_result)
        global_pos = parent_window.ui.forgot_password_button_settings.mapToGlobal(QPoint(0,0))
        confirmation_window.move(global_pos.x(), global_pos.y() + parent_window.ui.forgot_password_button_settings.height())
        confirmation_window.start_time()
        confirmation_window.show()

    def capture_result(self):
        parent_window = self._parent
        parent_window.ui.current_password_line.hide()
        parent_window.ui.new_password_line.clear()
        self.objective = 1

class Delete_user_account():
    def __init__(self, parent):
        self._parent = parent
        self.query = query_processor()

    def delete_user_signals_connect(self):
        parent_window = self._parent
        parent_window.ui.delete_user_button_2.clicked.connect(self.delete_user)

    def delete_user(self):
        parent_window = self._parent
        current_password = self._parent.ui.delete_user_line.text()

        # this needs to be a single func
        hash_password = self.query.get_hashed_password(userID=parent_window.userID)[0]
        compare = self.password_manager.check_password(current_password, hash_password)
        if compare:
            self.query.delete_user(parent_window.userID)
            parent_window.log_out()

class Change_category():
    def __init__(self, parent):
        self._parent = parent
        self.home_page = Home_page(parent)
        self.signals_connect()

    def signals_connect(self):
        self._parent.ui.category_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def show_category_table(self):
        parent_window = self._parent
        query = query_processor()
        if not parent_window.accountID:
            return

        self.categories = query.get_category_info(parent_window.userID, parent_window.accountID, asDF=True)

        if len(self.categories) == 0:
            self.set_category_table(False)
            parent_window.ui.no_categories_label.setText(f"No category found for '{parent_window.account_name}'")
        else:
            self.set_category_table(True)

            # -- TABLE LOADING -- 
            self.model = ListModelCategory(self.categories, parent_window, self)
            self.data = self.categories

            # Set the search filter for the table
            # inspired from:  https://www.youtube.com/watch?v=53bZSTSLUqI

            proxy_model = QSortFilterProxyModel()
            proxy_model.setSourceModel(self.model)
            proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
            proxy_model.setFilterKeyColumn(3)
            parent_window.ui.category_line.textChanged.connect(proxy_model.setFilterRegExp)
            parent_window.ui.category_table.setModel(proxy_model)

            hidden_columns = [0, 1]
            for i in hidden_columns:
                parent_window.ui.tableView.setColumnHidden(i, True)

            for row_index in range(len(self.categories)):
                category_id = self.categories.iloc[row_index].iloc[0]
                remove_button = QPushButton("Remove")
                remove_button.setObjectName("item_button")
                index_button = proxy_model.index(row_index, self.model.columnCount() - 1)
                parent_window.ui.category_table.setIndexWidget(index_button, remove_button)
                remove_button.clicked.connect(lambda clicked, id=category_id: self.handle_remove_button(id))


    def set_category_table(self, flag):
        parent_window = self._parent
        if flag:
            parent_window.ui.settings_stack.setCurrentWidget(parent_window.ui.category_table_page)
        else:
            parent_window.ui.settings_stack.setCurrentWidget(parent_window.ui.page_4)

    def handle_remove_button(self, categoryID):
        query = query_processor()
        query.remove_description_from_list_category(categoryID)
        query.update_transaction_after_deletion_description(categoryID)
        self.show_category_table()
        self.home_page.show_table()
