from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QTabWidget
from PyQt5.QtCore import Qt, pyqtSignal
from core.auth import register_user, login_user

class LoginWindow(QWidget):
    login_success = pyqtSignal(int, bytes)  # user_id, key

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Password Manager - Login/Register")
        self.setFixedSize(400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        tab_widget = QTabWidget()
        
        # Login Tab
        login_tab = QWidget()
        login_layout = QVBoxLayout()
        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Username")
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Master Password")
        self.login_password.setEchoMode(QLineEdit.Password)
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.handle_login)
        login_layout.addWidget(self.login_username)
        login_layout.addWidget(self.login_password)
        login_layout.addWidget(login_btn)
        login_tab.setLayout(login_layout)
        
        # Register Tab
        register_tab = QWidget()
        register_layout = QVBoxLayout()
        self.reg_username = QLineEdit()
        self.reg_username.setPlaceholderText("Username")
        self.reg_password = QLineEdit()
        self.reg_password.setPlaceholderText("Master Password")
        self.reg_password.setEchoMode(QLineEdit.Password)
        self.reg_confirm = QLineEdit()
        self.reg_confirm.setPlaceholderText("Confirm Master Password")
        self.reg_confirm.setEchoMode(QLineEdit.Password)
        register_btn = QPushButton("Register")
        register_btn.clicked.connect(self.handle_register)
        register_layout.addWidget(self.reg_username)
        register_layout.addWidget(self.reg_password)
        register_layout.addWidget(self.reg_confirm)
        register_layout.addWidget(register_btn)
        register_tab.setLayout(register_layout)
        
        tab_widget.addTab(login_tab, "Login")
        tab_widget.addTab(register_tab, "Register")
        layout.addWidget(tab_widget)
        self.setLayout(layout)

    def handle_login(self):
        try:
            username = self.login_username.text()
            password = self.login_password.text()
            success, user_id, key, message = login_user(username, password)
            if success:
                self.login_success.emit(user_id, key)
                self.close()
            else:
                QMessageBox.warning(self, "Error", message)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Login failed: {str(e)}")

    def handle_register(self):
        try:
            username = self.reg_username.text()
            password = self.reg_password.text()
            confirm = self.reg_confirm.text()
            if password != confirm:
                QMessageBox.warning(self, "Error", "Passwords do not match")
                return
            success, message = register_user(username, password)
            if success:
                QMessageBox.information(self, "Success", message)
            else:
                QMessageBox.warning(self, "Error", message)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Registration failed: {str(e)}")