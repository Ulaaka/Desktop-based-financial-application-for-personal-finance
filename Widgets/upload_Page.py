import sys, shutil
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from Widgets.live_output_window import Live_output_window
from FILE_handling import file_handling
from Widgets.stream import Stream
from Widgets.thread_worker import Thread_worker
from decouple import config
from queries import query_processor
from Widgets.home_page import Home_page

class Upload_page():
    def __init__(self, parent):
        self._parent = parent
        self.home_page = Home_page(parent)

    def add_transaction(self):
        parent_window = self._parent
        query = query_processor()
        date = parent_window.ui.transaction_date_edit.date().toPyDate()
        type = parent_window.ui.transaction_type_combo.currentText()
        description = parent_window.ui.description_text.toPlainText()
        amount = int(parent_window.ui.amount_transaction_line.text())
        balance = int(parent_window.ui.balance_transaction_line.text())

        if date and type and description and amount:
            if not balance:
                balance = 0
            #transaction_list.append((accountID, self.file_ID, self.change_to_date(row[0]), row[1], row[2], category, Decimal(row[3]),  Decimal(row[4])))
            category = query.return_updated_category(parent_window.userID, parent_window.accountID, description)
            transaction_list = [(parent_window.accountID, 1, date, type, description, category, amount, balance)]
            query.insert_into_transactions(transaction_list)
            self.home_page.show_table()
        else:
            QMessageBox.warning(
            parent_window, "Error", "Password fill the required fields")
            return

    def upload_file(self):
        parent_window = self._parent
        if (not parent_window.accountID):
            QMessageBox.warning(parent_window, 'Error', 'Please create an account first')
            return

        file_paths, _ = QFileDialog.getOpenFileNames(parent_window, 'Open File', "", "CSV Files (*.csv);;PDF Files (*.pdf)")
        if file_paths:
            for file_path in file_paths:
                shutil.copy(file_path, config('FOLDER_PATH'))

        saved_stdout = sys.stdout
        self.print_output = Stream()
        self.live_output = Live_output_window(parent_window, saved_stdout)
        self.print_output.input_text.connect(self.get_output)
        sys.stdout = self.print_output

        # process the files
        files_process = file_handling(parent_window.userID, parent_window.accountID, parent_window.key)
        self.worker = Thread_worker(files_process.process_files_in_folder)
        self.worker.start()
        self.live_output.ui.textBrowser.adjustSize()
        self.live_output.adjustSize()
        self.live_output.show()

    def get_output(self, text):
        stripped_list = [line for line in text.splitlines() if line.strip() != ""]
        lines = "\n".join(stripped_list)
        self.live_output.ui.textBrowser.append(lines)