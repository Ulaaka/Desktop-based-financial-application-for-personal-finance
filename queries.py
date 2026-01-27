from database_connection import database
from datetime import datetime

class query_processor:
    def __init__(self):
        connection = database()
        self.db = connection.db
        self.cursor = connection.cursor

    def find_min_max(self, column, max_toggle=True):
        toggle = "MAX" if max_toggle else "MIN"

        query = f"SELECT {toggle}({column})from transactions"
        self.cursor.execute(query)
        output = self.cursor.fetchone()
        return output[0]
        

    # transfer toggle = if true find the total income
    # at least one of the transfer_toggle and max_toggle should be included
    def total_transfer_or_extreme_value(self, username, transfer_toggle=None, max_toggle=None, account_name=None, date_lower=None, date_upper=None):
        try:
            parameter = [username]

            toggle = "SUM"
            base_query = f"SELECT {toggle}(T.amount)" 

            body_query = """
                    FROM users U
                    JOIN accounts A ON A.userID = U.userID
                    JOIN transactions T ON T.accountID = A.accountID
                    WHERE U.username = %s
            """

            if (max_toggle is not None):
                toggle = "MAX" if max_toggle else "MIN"

            if (max_toggle is not None or transfer_toggle is not None):
                base_query =  f"SELECT ABS({toggle}(T.amount))" 

            query = base_query + body_query

            if (transfer_toggle is not None):
                toggle = ">" if transfer_toggle else "<"
                query+=f" and T.amount {toggle} 0"
            
            if (account_name is not None):
                query+= " and A.account_name = %s"
                parameter.append(account_name)

            if (date_lower):
                query += " and T.transaction_date >= %s"
                parameter.append(date_lower)

            if (date_upper):
                query += " and T.transaction_date <= %s"
                parameter.append(date_upper)

            self.cursor.execute(query, tuple(parameter))

            output = self.cursor.fetchone()
            print(output[0])
            return output[0]
        except:
            print("important arguments (max_toggle or transfer_toggle missing)")
    