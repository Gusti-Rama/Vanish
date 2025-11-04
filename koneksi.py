import os
import mysql.connector
import pandas as pd
from dotenv import load_dotenv  # untuk mengambil data dari file .env

load_dotenv()

def get_connection():
    """Create a new MySQL connection from environment variables."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=os.getenv("DB_PORT"),
        autocommit=False,
    )


# Di file koneksi.py

def run_query(query: str, params: tuple | None = None, fetch: bool = False):
    """Execute a SQL query.

    - When fetch=True, returns a pandas DataFrame (can be empty) or None on error.
    - When fetch=False, commits changes and returns True on success, False on error.
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        if params is not None:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        if fetch:
            rows = cursor.fetchall()
            return pd.DataFrame(rows)
        else:
            conn.commit()
            return True 
    except mysql.connector.Error as err: 
        print(f"Database Error: {err}") 
        if conn is not None:
            conn.rollback()
        
        if fetch:
            return None
        else:
            return False
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()
