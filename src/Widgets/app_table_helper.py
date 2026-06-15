from PyQt5.QtCore import QAbstractTableModel, Qt
from db_queries import QueryProcessor

"""
The following tables were inspired from:
https://www.pythonguis.com/faq/editing-pyqt6-tableview/

"""

class TransactionTable(QAbstractTableModel):
    """
    Table model for displaying and editing transaction records on the home page
    """
    def __init__(self, data, parent, home_page):
        super().__init__(parent)
        self._data = data
        self._parent = parent
        self.userID = parent.userID
        self.home_page = home_page
        self.header_names = ["Transaction ID", "Account ID", "File ID" , "Date", "Type", "Description", "Category", "Amount", "Balance"]

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        # add columns + extra column at the back
        return self._data.shape[1] + 1

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        """
        Returns the value for each cell, empty string for the extra button column
        """
        if index.isValid():
            if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
                column =int(index.column())
                if column < 9:
                    value = self._data.iloc[index.row(), index.column()]
                else:
                    value = ""
                return str(value)

    def setData(self, index, value, role):
        """
        Handles direct cell edits in the transaction table
        Column 5 triggers a description update and recalculates the category
        Column 6 triggers a direct category update for the transaction and related ones
        """
        query = QueryProcessor()
        main_window = self._parent
        if role == Qt.ItemDataRole.EditRole:
            column =int(index.column())
            row = int(index.row())
            transactionID = int(self._data.iloc[row, 0])
            self._data.iloc[index.row(), index.column()] = value
            # change category
            if column == 6:
                query.change_category_transaction(self.userID, main_window.accountID, value, transactionID)
                self.home_page.show_table()
            if column == 5:
                if query.change_transaction_description_and_update(main_window.userID, main_window.accountID, value, transactionID):
                    self.home_page.show_table()
            return True
        return False

    def headerData(self, col, orientation, role):
        """
        Returns the column header name, empty string for the button column
        """
        if (
            orientation == Qt.Orientation.Horizontal
            and role == Qt.ItemDataRole.DisplayRole
        ):
            if (col < 9):
                return self.header_names[col]
                #return self._data.columns[col]

            else:
                return ""

    def flags(self, index):
        return (
            Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsEditable
        )

class CategoryTable(QAbstractTableModel):
    """
    Table model for displaying and editing categories on the settings page
    The last row is reserved for creating a new category
    """
    def __init__(self, data, parent, category_page):
        super().__init__(parent)
        self._data = data
        self._parent = parent
        self.userID = parent.userID
        self.category_page = category_page
        self.description = None
        self.name = None
        self.header_names = ["Category ID", "Category List", "Description/Key Words", "Name"]

    def rowCount(self, index):
        # for adding new categories
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1] + 1  # keep your logic

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        """
        Returns the value for each cell, empty string for the extra button column
        """
        if index.isValid():
            if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):

                column = int(index.column())

                if column < self._data.shape[1]:
                    value = self._data.iloc[index.row(), index.column()]
                else:
                    value = "" 

                return str(value)

    def setData(self, index, value, role):
        """
        Handles direct cell edits in the category table
        Last row stores description and name temporarily until the add button is clicked
        For existing rows, editing description or name updates the category and re-matches transactions
        """
        query = QueryProcessor()
        main_window = self._parent
        if role == Qt.ItemDataRole.EditRole:

            column = int(index.column())
            row = int(index.row())
            categoryID = int(self._data.iloc[row, 0])
            self._data.iloc[row, column] = value
            # save the changes if its last row
            if row == self._data.shape[0] - 1:
                # category sentence change
                if column == 2:
                    self.description = value
                elif column == 3:
                    self.name = value
            else:
                if column == 2:
                    description = value
                    name = self._data.iloc[row, column+1]
                    close_transaction_ids, word_list = query.find_close_transactions_and_keywords(description, main_window.accountID)
                    query.update_category_description(description, word_list, name, categoryID)
                    query.update_category(name, close_transaction_ids)
                    self.category_page.show_category_table()

                elif column == 3:
                    name = value
                    description = self._data.iloc[row, column-1]
                    close_transaction_ids, word_list = query.find_close_transactions_and_keywords(description, main_window.accountID)
                    query.update_category_name(name, categoryID)
                    query.update_category(name, close_transaction_ids)
                    self.category_page.show_category_table()

            return True
        return False

    def headerData(self, col, orientation, role):
        """
        Returns the column header name, empty string for the button column
        """
        if (
            orientation == Qt.Orientation.Horizontal
            and role == Qt.ItemDataRole.DisplayRole
        ):
            if col < self._data.shape[1]:
                return self.header_names[col]
                #return self._data.columns[col]
            else:
                return ""

    def flags(self, index):
        return (
            Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsEditable
        )