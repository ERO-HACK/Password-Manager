from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QLabel, QMessageBox, QApplication, QHeaderView, QMenu, QAction
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QClipboard
from core.database import DatabaseManager
from core.encryption import decrypt
from ui.add_password_ui import AddPasswordDialog

class DashboardWindow(QMainWindow):
    def __init__(self, user_id, key):
        super().__init__()
        self.user_id = user_id
        self.key = key
        self.current_theme = "light"
        self.setWindowTitle("Password Manager - Dashboard")
        self.setFixedSize(800, 600)
        try:
            self.init_ui()
            self.load_passwords()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to initialize dashboard: {str(e)}")
            raise  # Re-raise to log in console

    def init_ui(self):
        try:
            central_widget = QWidget()
            layout = QVBoxLayout()

            # Search bar
            search_layout = QHBoxLayout()
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("Search by site or username...")
            self.search_input.textChanged.connect(self.filter_table)
            search_btn = QPushButton()
            search_btn.setIcon(QIcon("assets/icons/search.png"))
            search_btn.clicked.connect(self.filter_table)
            search_layout.addWidget(self.search_input)
            search_layout.addWidget(search_btn)

            # Table
            self.table = QTableWidget(0, 5)
            self.table.setHorizontalHeaderLabels(["ID", "Site/App", "Username", "Password", "Actions"])
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.table.setSelectionBehavior(QTableWidget.SelectRows)
            self.table.setContextMenuPolicy(Qt.CustomContextMenu)
            self.table.customContextMenuRequested.connect(self.show_context_menu)

            # Buttons
            btn_layout = QHBoxLayout()
            add_btn = QPushButton("Add Password")
            add_btn.setIcon(QIcon("assets/icons/add.png"))
            add_btn.clicked.connect(self.add_password)
            theme_btn = QPushButton("Switch Theme")
            theme_btn.setIcon(QIcon("assets/icons/theme.png"))
            theme_btn.clicked.connect(self.switch_theme)
            btn_layout.addWidget(add_btn)
            btn_layout.addWidget(theme_btn)

            layout.addLayout(search_layout)
            layout.addWidget(self.table)
            layout.addLayout(btn_layout)
            central_widget.setLayout(layout)
            self.setCentralWidget(central_widget)
        except Exception as e:
            raise Exception(f"UI initialization failed: {str(e)}")

    def load_passwords(self, filter_text=""):
        try:
            db = DatabaseManager()
            passwords = db.get_passwords(self.user_id)
            db.close()
            self.table.setRowCount(0)
            for pw in passwords:
                pw_id, site, username, enc_pw = pw
                dec_pw = decrypt(enc_pw, self.key)
                if dec_pw is None:
                    raise ValueError(f"Failed to decrypt password for site: {site}")
                if filter_text.lower() not in site.lower() and filter_text.lower() not in username.lower():
                    continue
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(pw_id)))
                self.table.setItem(row, 1, QTableWidgetItem(site))
                self.table.setItem(row, 2, QTableWidgetItem(username))
                self.table.setItem(row, 3, QTableWidgetItem("********"))  # Masked
                action_btn = QPushButton()
                action_btn.setIcon(QIcon("assets/icons/copy.png"))
                action_btn.setIconSize(QSize(16, 16))
                action_btn.setFixedSize(40, 30)
                action_btn.setStyleSheet("background-color: #3498db; color: white; border-radius: 5px; padding: 2px;")
                action_btn.setToolTip("Copy password to clipboard")
                action_btn.clicked.connect(lambda _, p=dec_pw: self.copy_to_clipboard(p))
                self.table.setCellWidget(row, 4, action_btn)
        except Exception as e:
            raise Exception(f"Failed to load passwords: {str(e)}")

    def filter_table(self):
        try:
            self.load_passwords(self.search_input.text())
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to filter table: {str(e)}")

    def add_password(self):
        try:
            dialog = AddPasswordDialog(self.user_id, self.key, self)
            if dialog.exec_():
                self.load_passwords()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add password: {str(e)}")

    def edit_password(self, row):
        try:
            pw_id = int(self.table.item(row, 0).text())
            site = self.table.item(row, 1).text()
            username = self.table.item(row, 2).text()
            db = DatabaseManager()
            passwords = db.get_passwords(self.user_id)
            enc_pw = next(p[3] for p in passwords if p[0] == pw_id)
            db.close()
            dec_pw = decrypt(enc_pw, self.key)
            if dec_pw is None:
                raise ValueError(f"Failed to decrypt password for editing ID {pw_id}")
            dialog = AddPasswordDialog(self.user_id, self.key, self, edit_mode=True, site=site, username=username, password=dec_pw, pw_id=pw_id)
            if dialog.exec_():
                self.load_passwords()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to edit password: {str(e)}")

    def delete_password(self, row):
        try:
            pw_id = int(self.table.item(row, 0).text())
            if QMessageBox.question(self, "Confirm", "Delete this entry?") == QMessageBox.Yes:
                db = DatabaseManager()
                db.delete_password(pw_id)
                db.close()
                self.load_passwords()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete password: {str(e)}")

    def copy_to_clipboard(self, text):
        try:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            QMessageBox.information(self, "Success", "Copied to clipboard!", QMessageBox.Ok)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to copy to clipboard: {str(e)}")

    def show_context_menu(self, pos):
        try:
            row = self.table.rowAt(pos.y())
            if row == -1:
                return
            menu = QMenu()
            edit_action = QAction(QIcon("assets/icons/edit.png"), "Edit", self)
            edit_action.triggered.connect(lambda: self.edit_password(row))
            delete_action = QAction(QIcon("assets/icons/delete.png"), "Delete", self)
            delete_action.triggered.connect(lambda: self.delete_password(row))
            menu.addAction(edit_action)
            menu.addAction(delete_action)
            menu.exec_(self.table.viewport().mapToGlobal(pos))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to show context menu: {str(e)}")

    def switch_theme(self):
        try:
            if self.current_theme == "light":
                self.current_theme = "dark"
                self.setStyleSheet(self.get_dark_stylesheet())
            else:
                self.current_theme = "light"
                self.setStyleSheet(self.get_light_stylesheet())
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to switch theme: {str(e)}")

    def get_light_stylesheet(self):
        return """
        QMainWindow { background: #f0f0f0; }
        QTableWidget { background: white; border: 1px solid #ddd; }
        QPushButton { background: #4CAF50; color: white; border-radius: 5px; }
        QPushButton:hover { background: #45a049; }
        """

    def get_dark_stylesheet(self):
        return """
        QMainWindow { background: #333; color: #ddd; }
        QTableWidget { background: #444; border: 1px solid #555; }
        QPushButton { background: #555; color: #ddd; border-radius: 5px; }
        QPushButton:hover { background: #666; }
        """