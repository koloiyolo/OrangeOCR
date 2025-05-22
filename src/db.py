import sqlite3
import pandas as pd

database_file = 'database.db'


def init_db():
    """
    Initializes database schema if
    database doesn't exist
    :return:
    """
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS data (
            nr TEXT,
            miesiac TEXT,
            netto REAL,
            brutto REAL
            )
        """)
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                nr TEXT,
                name TEXT,
                department REAL,
                account REAL
                )
            """)
    conn.commit()
    conn.close()


def save_to_database(month, df):
    try:
        init_db()
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()

        for _,row in df.iterrows():
            cursor.execute("""
                                    INSERT INTO data (nr, miesiac, netto, brutto)
                                    VALUES (?, ?, ?, ?)
                                """, (row['nr'], month, row['netto'], row['brutto']))

        conn.commit()
        conn.close()

    except sqlite3.Error as e:
        print(f"Error executing query: {e}")

def execute(statement, params=None):
    """
    Executes SQL statement and returns output as
    DataFrame.
    :param statement: SQL statement to execute
    :param params: (optional) params for SQL statement
    :return:
    """
    try:
        init_db()
        df = None
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()

        if params:
            cursor.execute(statement, params)
        else:
            cursor.execute(statement)

        rows = cursor.fetchall()
        columns = None
        if rows:
            columns = [desc[0] for desc in cursor.description]

        conn.commit()
        conn.close()

        if columns:
            df = pd.DataFrame(rows, columns=columns)
            return df
        return True

    except sqlite3.Error as e:
        print(f"Error executing query: {e}")
        return False
