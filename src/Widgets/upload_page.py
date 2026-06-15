import sys, shutil
from datetime import date
from decouple import config

from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import QDate, pyqtSignal, QObject

from Widgets.live_output_window import LiveOutputWindow
from Widgets.thread_worker import ThreadWorker

from db_queries import QueryProcessor
from file_handle import FileHandling

class UploadPage():
    """
    Class for handling the transactions uploading by uploading files and individually adding transactions
    """
    def __init__(self, parent):
        """
        Constructor for upload page
        """
        self._parent = parent
        self.current_date = date.today()
        self.upload_signals_connect()

    def upload_signals_connect(self):
        """
        Connects the signals
        """
        parent_window = self._parent
        parent_window.ui.upload_file_button.clicked.connect(self.upload_file)
        parent_window.ui.add_transaction_button.clicked.connect(self.add_transaction)

    def add_transaction(self):
        """
        Manages the individual transaction uploading
        - Validates the fields.
        - Updates the category of the transaction with the best matching category in the database.
        - Updates the transaction table after insertion and clears the fields.
        """

        parent_window = self._parent
        query = QueryProcessor()
        # Check if account is created
        if parent_window.accountID is None:
            QMessageBox.warning(
            parent_window, "Error", "Please create an account first")
            return

        # Check if required transaction entries are filled
        try:
            date_input = parent_window.ui.transaction_date_edit.date().toPyDate()
            type = parent_window.ui.transaction_type_combo.currentText()
            description = parent_window.ui.description_text.toPlainText()
            amount = int(parent_window.ui.amount_transaction_line.text())
            balance = int(parent_window.ui.balance_transaction_line.text())
        except:
            QMessageBox.warning(
            parent_window, "Error", "Password fill the required fields")
            return

        if date_input and type and description and amount:
            # When balance not entered, set to 0
            if not balance:
                balance = 0
            # The transaction data can not be in the future
            if date_input > self.current_date:
                self.clear_fields()
                QMessageBox.warning(
                parent_window, "Error", "Entered date is not valid")
                return

            # Get the updated category of the transaction
            category = query.return_updated_category(parent_window.userID, parent_window.accountID, description)

            transaction_list = [(parent_window.accountID, None, date_input, type, description, category, amount, balance)]
            query.insert_into_transactions(transaction_list)

            # Clear the fields once inserted
            self.clear_fields()

            # Update the transaction table with new transaction
            self._parent.home_manager.show_table()

    def clear_fields(self):
        """
        Clears the individual transaction uploading fields
        """
        parent_window = self._parent
        parent_window.ui.transaction_date_edit.setDate(QDate(self.current_date .year, self.current_date .month, self.current_date .day))
        parent_window.ui.description_text.clear()
        parent_window.ui.amount_transaction_line.clear()
        parent_window.ui.balance_transaction_line.clear()

    def upload_file(self):
        """
        Manages transaction files uploading
        - Allows the user to upload the files using native system
        - Assigns file processing function to the thread worker to keep the app responsive during the files processing
        - Shows uploaded files status on a window
        """

        parent_window = self._parent

        # Check if account is created
        if (not parent_window.accountID):
            QMessageBox.warning(parent_window, 'Error', 'Please create an account first')
            return

        # Enables native file system, restricting file types to CSV ans PDF
        file_paths, _ = QFileDialog.getOpenFileNames(parent_window, 'Open File', "", "CSV Files (*.csv);;PDF Files (*.pdf)")
        if file_paths:
            for file_path in file_paths:
                shutil.copy(file_path, config('FOLDER_PATH'))

        saved_stdout = sys.stdout

        # Capture the print statements
        self.print_output = Stream()
        self.live_output = LiveOutputWindow(parent_window, saved_stdout)
        sys.stdout = self.print_output

        files_process = FileHandling(parent_window.userID, parent_window.accountID, parent_window.key)

        # Submits the files processing function to the Worker thread
        self.worker = ThreadWorker(files_process.process_files_in_folder)

        # Start the thread worker
        self.worker.start()

        # When finished connect to the live output to show uploaded files status
        self.print_output.input_text.connect(self.get_output)
        self.live_output.ui.textBrowser.adjustSize()
        self.live_output.adjustSize()
        self.live_output.show()

    def get_output(self, text):
        stripped_list = [line for line in text.splitlines() if line.strip() != ""]
        lines = "\n".join(stripped_list)
        self.live_output.ui.textBrowser.append(lines)

class Stream(QObject):
    """
    Custom class for capturing print outputs
    """
    input_text = pyqtSignal(str)

    def write(self, text):
        self.input_text.emit(text)

    def flush(self):
        sys.stdout.flush()