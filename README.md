Money Manager Application:

A personal finance app that reads the bank statements and turns them into clear, interactive charts and reports to get a better understanding of financial pattern.

Setting up:

- Install the dependencies:
```bash
pip install -r requirements.txt
```

- Set up the environment variables and fill the values in your env:
```bash
cp .env.example .env
```

- Set up the database:
```bash
mysql -u root -p < database_creation_query.sql
```

- Run the application:
```bash
python src/main.py
```

Features:

- Supports PDF and CSV bank statements from multiple UK banks (Lloyds, HSBC, Monzo, Santander etc.)
- Automatically standardises transaction data across different bank formats
- Searchable and filterable transaction table
- Smart auto-categorisation that updates as changes are made
- Nine types of interactive charts and graphs
- Export everything as CSV, PDF, or PNG
- Files are encrypted on disk and passwords are hashed
- Recovers the account including access to the uploaded files

Login Page
