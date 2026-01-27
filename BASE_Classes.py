import dateutil.parser
from datetime import datetime
import bcrypt


class ParsingBase:
    def check_date_type(self, dateList):
        try:
            datetime.strptime(dateList[0], "%d/%m/%Y")
            return True
        except ValueError:
            return False
        
    # https://stackoverflow.com/questions/52206973/convert-different-date-formats-to-a-given-unique-date-format-in-python
    def change_type(self, dateList, column, dataframe):
        if not self.check_date_type(dateList):
            for i in column:
                column = column.replace([i], dateutil.parser.parse(i).strftime("%d/%m/%Y"))
        dataframe[dataframe.columns[0]] = column

    def unify_amount_columns(self, df):
        same = df[df.columns[-3]].equals(df[df.columns[-2]])
        
        if (same):
            df.drop(df.columns[[-3]], axis=1, inplace=True)
        else:
            corrected = (df[df.columns[-3]].fillna(0) - df[df.columns[-2]].fillna(0))
            pos = len(df.columns) - 3
            df.insert(pos, "Amount", corrected)
            df.drop(columns=[df.columns[-3], df.columns[-2]], inplace=True)

    def order_dataframe(self, df, columns):
        missing = sorted(list(set(range(6)) - set(columns)))

        if (not missing):
            return df
        print("missing values:\n")
        print(missing)

        extra = 0
        for i in missing:
            pos = i + extra
            if (i == 1):
                df.insert(pos, "Type", "")
            elif (i == 2):
                df.insert(pos, "Description", "")
            else:
                raise Exception("Important column is not selected")
            extra+=1
        return df

class password_class:
    
    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # later used to check the password
    def check_password(self, plain_text_password, hashed_password):
        return bcrypt.checkpw(plain_text_password, hashed_password)
    
