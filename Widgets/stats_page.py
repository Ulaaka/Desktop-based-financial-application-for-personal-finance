import sys, shutil
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import QDate
from Widgets.live_output_window import Live_output_window
from FILE_handling import file_handling
from Widgets.stream import Stream
from Widgets.thread_worker import Thread_worker
from decouple import config
from queries import query_processor
from Widgets.home_page import Home_page
from datetime import date
class Stats_page():
    def __init__(self, parent):
        self._parent = parent
        self.set_chart_view = None

        # active chart name
        self.chart_name = None
        # graph to filters
        self.active_filters = None
        # active graph buttons
        self.active_buttons = []
        # dates
        self.upper_date = None
        self.lower_date = None

        # filter (labels, names)
        self.filters_map = {
            "transaction_type": { 
                "Transaction Type", ["All", "Income", "Expense"]
            },
            "measure_type": {
                "Mode", ["Total", "Incoming", "Outgoing"]
            },
            "date_type": {
                "Date Range", ["From", "To"]
            }
        }

        # graph to filter
        self.graph_to_filter = {
            "Summary" : ["transaction_type", "measure_type", "date_type"],
            "Monthly Trend": ["measure_type", "date_type"],
            "Weekly Trend": ["measure_type", "date_type"],
            "Yearly Trend": ["measure_type", "date_type"],
            "Distribution": ["transaction_type", "date_type"]
        }

    def stats_signals_connect(self):
        pass
