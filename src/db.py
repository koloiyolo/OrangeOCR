import sqlite3
import pandas as pd

database_file = 'database.db'


def init_db():
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


def read_database(month):
    try:
        init_db()
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()

        if month:
            sql_query = """
                            SELECT u.nr, u.name, u.department, u.account, d.netto, d.brutto
                            FROM users u
                            LEFT JOIN data d ON u.nr = d.nr
                            WHERE d.miesiac = ?
                            UNION
                            SELECT NULL, NULL, 'Konto: ', u.account AS konto, ROUND(SUM(d.netto), 2) AS Netto, ROUND(SUM(d.brutto), 2) AS Brutto
                            FROM users u
                            LEFT JOIN data d ON u.nr = d.nr
                            WHERE d.miesiac = ?
                            GROUP BY u.account
                            UNION
                            SELECT NULL, NULL, NULL, 'Razem:', ROUND(SUM(d.netto), 2) AS Netto, ROUND(SUM(d.brutto), 2) AS Brutto
                            FROM users u
                            LEFT JOIN data d ON u.nr = d.nr
                            WHERE d.miesiac = ?
                        """

            cursor.execute(sql_query, (month, month, month))
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(rows, columns=columns)
            conn.close()
            return df

        else:

            sql_query = """
                            SELECT u.nr, u.name, u.department, u.account, SUM(d.netto), SUM(d.brutto)
                            FROM users u
                            LEFT JOIN data d ON u.nr = d.nr
                            GROUP BY u.nr, u.name, u.department, u.account
                            UNION
                            SELECT NULL, NULL, 'Konto: ', u.account AS konto, ROUND(SUM(d.netto), 2) AS Netto, ROUND(SUM(d.brutto), 2) AS Brutto
                            FROM users u
                            LEFT JOIN data d ON u.nr = d.nr
                            GROUP BY u.account
                            UNION
                            SELECT NULL, NULL, NULL, 'Razem:', ROUND(SUM(d.netto), 2) AS Netto, ROUND(SUM(d.brutto), 2) AS Brutto
                            FROM users u
                            LEFT JOIN data d ON u.nr = d.nr
                        """

            cursor.execute(sql_query)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(rows, columns=columns)
            conn.close()
            return df

    except sqlite3.Error as e:
        print(f"Error executing query: {e}")


def delete_from_database(month):
    try:
        init_db()
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()
        cursor.execute("""
                       DELETE FROM data
                       WHERE miesiac = ? 
                       """, (month,))
        conn.commit()
        conn.close()

    except sqlite3.Error as e:
        print(f"Error executing query: {e}")


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