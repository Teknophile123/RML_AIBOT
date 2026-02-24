import pyodbc

def get_db_connection():
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=.\SQLEXPRESS;"
        "DATABASE=10Feb_2026RML;"
        "Trusted_Connection=yes;"

    )
    return conn
