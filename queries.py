from database_connection import database
from datetime import datetime

class query_processor:
    def __init__(self):
        connection = database()
        self.db = connection.db
        self.cursor = connection.cursor

    # find extreme value of the column [amount, transaction_date, balance]
    def find_min_max(self, column, max_toggle=True):
        toggle = "MAX" if max_toggle else "MIN"

        query = f"SELECT {toggle}({column}) from transactions"
        self.cursor.execute(query)
        output = self.cursor.fetchone()
        return output[0]
        
    # transfer toggle = if true find the total income
    def total_transfer(self, username, transfer_toggle, account_name=None, date_lower=None, date_upper=None):
        parameter = [username]

        query = """
            SELECT ABS(SUM(T.amount)) as total_expense
            FROM users U
            JOIN accounts A ON A.userID = U.userID
            JOIN transactions T ON T.accountID = A.accountID
            WHERE U.username = %s
        """

        transfer_additional = " and T.amount > 0" if transfer_toggle else " and T.amount < 0"
        query+=transfer_additional
        
        if (account_name is not None):
            query+= " and A.account_name = %s"
            parameter.append(account_name)

        date_additional = "and T.transaction_date BETWEEN %s and %s"

        if (date_lower and date_upper):
            query+=date_additional
            parameter.extend([date_lower, date_upper])

        elif (date_upper):
            date_lower = self.find_min_max("transaction_date", False)
            query+=date_additional
            parameter.extend([date_lower, date_upper])

        elif (date_lower):
            date_upper = self.find_min_max("transaction_date", True)
            query+=date_additional
            parameter.extend([date_lower, date_upper])

        self.cursor.execute(query, tuple(parameter))

        output = self.cursor.fetchone()
        print(output[0])
        return output[0]
    
    