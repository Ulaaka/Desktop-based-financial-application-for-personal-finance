from CSV_Parser import ParsingCSV
from DF_Processor import ProcessingDF
from HSBC_Pdf_Parser import HSBC_PDF_CONVERSION
from PDF_Parser import ParsingPDF
from queries import query_processor


#parsing = ParsingCSV("Monzo_csv.csv")
# Monzo_pdf
# TXN_pdf
# 2025_October_Statement
# 2025_September_Statement
#parsing = ParsingPDF("TXN_pdf.pdf")

#parsing = HSBC_PDF_CONVERSION("2025-06-20_Statement.pdf")
#processor = ProcessingDF(parsing.df, "test5", "Ulaaka_1223", "urnaa@gmail.com", "savings", "Bank", "GBP")
#converted = ParsingPDF("Statement_12_2025.pdf")

query = query_processor()
#date_upper="2025-06-03"
query.total_transfer_or_extreme_value("test5", "2025-06-03")


#last_day = query.return_last_month("2025-11-13")

# exp = query.compare_range("test5", False, "savings", "2025-11-07", "2025-12-23", "date")

#query.common_transactions("test5",  5, account_name="savings",transfer_toggle=False, date_lower="2025-12-23", filter_amount=5)

