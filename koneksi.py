import os
import mysql.connector
import pandas as pd
from dotenv import load_dotenv  # ambil data dr .env

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=os.getenv("DB_PORT"),
        autocommit=False,
    )

def run_query(query: str, params: tuple | None = None, fetch: bool = False):
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
