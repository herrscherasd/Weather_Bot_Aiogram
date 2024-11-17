import sqlite3

class CustomDB:
    def __init__(self):
        self.connect = sqlite3.connect("users.db")
        
    def connect_db(self):
        cursor = self.connect.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            username VARCHAR(255),
            first_name VARCHAR(255),
            last_name VARCHAR(255),
            id INTEGER,
            
            created VARCHAR(100)
            );""")
         
        cursor.execute("""CREATE TABLE IF NOT EXISTS address (
            id_user INTEGER,
            address_longitude REAL,
            address_latitude REAL,
            timestamp DATETIME
            );""")
        self.connect.commit()