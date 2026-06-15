from PyQt5.QtCore import QThread, pyqtSignal
# https://realpython.com/python-pyqt-qthread/
class ThreadWorker(QThread):
    """
    Class for thread worker
    It gets assigned computation heavy function to keep the main app responsive during the execution.
    """
    done = pyqtSignal()

    def __init__(self, todo):
        """
        Constructor for thread worker.
        """
        super().__init__()
        self.function = todo

    def run(self):
        """
        Runs the functions and emits a signal when finished.
        """
        self.function()
        self.done.emit()