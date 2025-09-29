import sqlite3
import os

DB_PATH = "passwords.db"

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                salt BLOB NOT NULL,
                verification BLOB NOT NULL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                site TEXT NOT NULL,
                username TEXT NOT NULL,
                encrypted_password BLOB NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        self.conn.commit()

    def insert_user(self, username, salt, verification):
        self.cursor.execute("INSERT INTO users (username, salt, verification) VALUES (?, ?, ?)", (username, salt, verification))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_user(self, username):
        self.cursor.execute("SELECT id, salt, verification FROM users WHERE username = ?", (username,))
        return self.cursor.fetchone()

    def insert_password(self, user_id, site, username, encrypted_password):
        self.cursor.execute("INSERT INTO passwords (user_id, site, username, encrypted_password) VALUES (?, ?, ?, ?)", (user_id, site, username, encrypted_password))
        self.conn.commit()

    def get_passwords(self, user_id):
        self.cursor.execute("SELECT id, site, username, encrypted_password FROM passwords WHERE user_id = ?", (user_id,))
        return self.cursor.fetchall()

    def update_password(self, pw_id, site, username, encrypted_password):
        self.cursor.execute("UPDATE passwords SET site = ?, username = ?, encrypted_password = ? WHERE id = ?", (site, username, encrypted_password, pw_id))
        self.conn.commit()

    def delete_password(self, pw_id):
        self.cursor.execute("DELETE FROM passwords WHERE id = ?", (pw_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()