import sys
from PyQt5.QtWidgets import QDialog

from generated_files.live_output_generated import Ui_live_output_window
from file_handle import FileHandling
from base_classes import CryptoHelper
from db_queries import QueryProcessor

class LiveOutputWindow(QDialog):
    """
    Dialog window that displays the upload output messages
    Also allows the user to click on duplicate files to preview them
    """
    def __init__(self, parent, saved_print):
        super().__init__(parent)
        self._parent = parent
        self.key = parent.key
        self.accountID = parent.accountID
        self.userID = parent.userID
        self.saved_print = saved_print

        self.ui = Ui_live_output_window()
        self.crypto = CryptoHelper()
        self.file_handle = FileHandling(self.userID, self.accountID, self.key)
        self.query = QueryProcessor()

        self.ui.setupUi(self)
        self.live_output_signals_connection()

    def live_output_signals_connection(self):
        """
        Connects the text browser signals for dynamic resizing and clickable file links
        """
        self.setObjectName('live_output_window')
        self.ui.textBrowser.setOpenLinks(False)
        self.ui.textBrowser.textChanged.connect(self.adjust_text_edit)
        self.ui.textBrowser.anchorClicked.connect(self.link_click)

    def adjust_text_edit(self):
        """
        Resizes the text browser height to fit its content as new text is added
        """
        text = self.ui.textBrowser.document()
        text.adjustSize()
        self.ui.textBrowser.setMinimumHeight(int(text.size().height()))

    # Action when the link in the text is clicked
    def link_click(self, event):
        """
        Opens a temporary preview of the file when its link is clicked in the text browser
        :param event: the clicked link containing the original filename
        """
        flag = False
        pressed_file_name = event.toString()
        original_filename = pressed_file_name.split(":")[1]

        self.file_handle.view_file(original_filename)

    # when the file window close
    def closeEvent(self, event):
        """
        Cleans up any temporary decrypted files and restores stdout when the window closes
        """
        for file in self.file_handle.temp_files:
            self.file_handle.delete_temp_file(file)
        event.accept()
        sys.stdout = self.saved_print
