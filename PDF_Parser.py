import camelot, re, pdfplumber, pandas as pd

from base_classes import ParsingHelper

class ParsingPDF:

    """
    Parses the file with pdf format
    """

    def __init__(self, pdf_name):
        """
        Constructor for pdf parsing class
        Finds the flavor the PDF, detect tables, cleans them up and save in self.df
        """

        flavor_choice = self.flavor_decision(pdf_name)
        tables = self.run_camelot(pdf_name, flavor_choice)
        self.parser = ParsingHelper()
        self.df = []
        for idx, table in enumerate(tables):
            df = table.df
            dataframes = self.clean_up(df, idx)
            for dataframe in dataframes:
                # Target columns
                columns = self.parser.choose_ratio(dataframe.columns.tolist())

                dataframe = dataframe[columns[0]]
                new_dataframe = self.parser.order_dataframe(dataframe, columns[1])
                new_dataframe = self.parser.unify_amount_columns(new_dataframe)

                money_columns = [new_dataframe.columns[-1], new_dataframe.columns[-2]]
                for i in money_columns:
                    dataframe[i] = pd.to_numeric(new_dataframe[i].astype(str).str.replace(',', ''), errors='coerce')

                self.df.append(new_dataframe)

    def find_header(self, df):
        """
        Selects the header of the dataframe
        by checking the requirements

        1. Unique
        2. All str
        3. Should be the same size as the rest of the columns
        :return: the position of the header in the original dataframe
        """

        # Check within the first 15 lines
        for i in range(min(15, len(df))):
            row = df.iloc[i]

            header_Values = row.tolist()
            string = True
            unique = True
            length = True
            length_count = 0
            for item in header_Values:
                if(item != ''):
                    length_count+=1

            for j in header_Values:
                if type(j) != str:
                    string = False

            if len(header_Values) > len(set(header_Values)):
                unique = False

            if (length_count != len(df.columns)):
                length = False

            if (string == True and unique == True and length == True):
                return i
        return 0

    def pre_clean_up(self, value):
        """
        Detects and removes extra special characters in the dataframe item

        :return: cleaned dataframe item
        """
        if value is None or not value or not isinstance(value, str):
            return value

        if (value[-1] == "."):
            value = value[:-1]

        if ("\n" in value):
            value = value.split("\n")[-1]

        value = re.sub(r'[^A-Za-z0-9 -./]+', '', value)
        try:
            value = float(value.replace(",", "").replace('"', ""))
        except:
            pass

        return value

    def clean_up(self, df, idx):
        """
        Cleans dataframe/s extracted from pdf pages, by checking the validity and requirements

        :return: list of cleaned dataframe
        """
        # Drops duplicate rows
        df = df.drop_duplicates()

        # apply to each item
        df = df.map(self.pre_clean_up)

        header = self.find_header(df)
        df.columns = df.iloc[header]
        df = df.reset_index(drop=True)

        dataframe_list = []
        rows_to_drop = []

        # Find rows where there is no number
        for j in range(len(df)):
            has_numbers = False
            row = df.iloc[j].tolist()
            for item in row:
                try:
                    float(item)
                    has_numbers = True
                    break
                except:
                    continue

            if (has_numbers == False):
                rows_to_drop.append(j)

        # Drop rows where there is no number
        df = df.drop(rows_to_drop)
        df = df.reset_index(drop=True)

        if not df.empty:
            test_value = df.loc[0, df.columns[0]]
            self.parser.change_date_type(test_value, df[df.columns[0]], df)
            dataframe_list.append(df)

        return dataframe_list

    def run_camelot(self, name, flavor_camelot):
        """
        Read pdf based on the given flavor and return the detected tables

        :return: detected table/s in a list
        """

        ROW_TOLERANCE = 20
        LINE_SCALE = 40

        if (flavor_camelot == "stream"):
            tables = camelot.read_pdf(name, flavor=flavor_camelot ,pages='all', row_tol = ROW_TOLERANCE)
        else:
            tables = camelot.read_pdf(name, flavor=flavor_camelot, pages='all', line_scale=LINE_SCALE)
        return tables

    def flavor_decision(self, name):
        """
        Chooses the right method for extracting dataframe from pages of pdf
        after detecting number of rectangles

        "stream": when the borders of table is absent, vague or unorganised
        "lattice": when the table is formatted clearly

        The flavor decision is made based on rectangles count on page 0 "PAGE_NUMBER"
        to allow for fast decision making

        :param name: name of the file
        :param idx: page number

        :return: the flavor decision
        """

        # min number of rectangles for "lattice" mode
        MIN_COUNT = 15
        PAGE_NUMBER = 0
        with pdfplumber.open(name) as pdf:
            page = pdf.pages[PAGE_NUMBER]
            # The size of rectangles
            header_rects = [
            r for r in page.rects
            if r['height'] > 5
            and r['height'] < 100
            and r['width'] < 200
        ]
        if len(header_rects) > MIN_COUNT:
            return "lattice"
        return "stream"
