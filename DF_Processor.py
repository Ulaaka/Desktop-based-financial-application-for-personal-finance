from datetime import datetime
from decimal import Decimal

from db_queries import QueryProcessor
from db_connection import Database
from base_classes import ParsingHelper

class ProcessingDF:

    """
    Processes the dataframe/s returned from parsing and inserts transactions into the database
    """

    def __init__(self, df, file_ID, userID, accountID):
        """
        Constructor for dataframe processing class
        """

        connection = Database()
        self.db = connection.db
        self.cursor = connection.cursor
        self.accountID = accountID
        self.file_ID = file_ID
        self.userID = userID

        if isinstance(df, list):
            for i in df:
                self.insert_transaction(self.accountID, i)
        else:
            self.insert_transaction(self.accountID, df)

    def insert_transaction(self, accountID, dtb):
        """
        Inserts transactions of dataframe/s after updating their category and date columns
        :param accountID: account ID to be inserted into
        :param dtb: dataframe/s  containing transaction to insert
        """
        parser = ParsingHelper()
        query = QueryProcessor()

        transaction_list = []
        for _, row in dtb.iterrows():
            row = list(map(str, row.tolist()))

            # return updated category
            category = query.return_updated_category(self.userID, self.accountID, row[2])
            row[1] = parser.classify_transaction_type(row[1])

            # Creates a list of transaction to allow for executing many for better runtime/performance
            transaction_list.append((accountID, self.file_ID, self.change_to_date(row[0]), row[1], row[2], category, Decimal(row[3]),  Decimal(row[4])))

        query.insert_into_transactions(transaction_list)

    def change_to_date(self, date_string):
        """
        Converts string date into a valid datetime date

        :param date_string: string date to be changed into datetime format
        :return: datetime formatted date 
        """
        date = datetime.strptime(date_string, "%d/%m/%Y")
        return date


