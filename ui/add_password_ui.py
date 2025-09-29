from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QCheckBox, QSpinBox, QLabel, QMessageBox
from PyQt5.QtGui import QIcon
from core.password_gen import generate_password
from core.database import DatabaseManager
from core.encryption import encrypt

class AddPasswordDialog(QDialog):
    def __init__(self, user_id, key, parent=None, edit_mode=False, site="", username="", password="", pw_id=None):
        super().__init__(parent)
        self.user_id = user_id
        self.key = key
        self.edit_mode = edit_mode
        self.pw_id = pw_id
        self.setWindowTitle("Add Password" if not edit_mode else "Edit Password")
        self.setFixedSize(400, 300)
        self.init_ui(site, username, password)

    def init_ui(self, site, username, password):
        layout = QVBoxLayout()
        
        self.site_input = QLineEdit(site)
        self.site_input.setPlaceholderText("Site/App")
        self.username_input = QLineEdit(username)
        self.username_input.setPlaceholderText("Username")
        self.password_input = QLineEdit(password)
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        
        # Generator options
        gen_layout = QVBoxLayout()
        length_label = QLabel("Password Length:")
        self.length_spin = QSpinBox()
        self.length_spin.setRange(8, 32)
        self.length_spin.setValue(16)
        self.upper_check = QCheckBox("Uppercase")
        self.upper_check.setChecked(True)
        self.lower_check = QCheckBox("Lowercase")
        self.lower_check.setChecked(True)
        self.digits_check = QCheckBox("Digits")
        self.digits_check.setChecked(True)
        self.symbols_check = QCheckBox("Symbols")
        self.symbols_check.setChecked(True)
        gen_btn = QPushButton("Generate")
        gen_btn.setIcon(QIcon("assets/icons/generate.png"))
        gen_btn.clicked.connect(self.generate_pw)
        
        gen_options = QHBoxLayout()
        gen_options.addWidget(length_label)
        gen_options.addWidget(self.length_spin)
        gen_options.addWidget(self.upper_check)
        gen_options.addWidget(self.lower_check)
        gen_options.addWidget(self.digits_check)
        gen_options.addWidget(self.symbols_check)
        gen_layout.addLayout(gen_options)
        gen_layout.addWidget(gen_btn)
        
        save_btn = QPushButton("Save" if not self.edit_mode else "Update")
        save_btn.clicked.connect(self.save_password)
        
        layout.addWidget(self.site_input)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addLayout(gen_layout)
        layout.addWidget(save_btn)
        self.setLayout(layout)

    def generate_pw(self):
        try:
            pw = generate_password(
                self.length_spin.value(),
                self.upper_check.isChecked(),
                self.lower_check.isChecked(),
                self.digits_check.isChecked(),
                self.symbols_check.isChecked()
            )
            self.password_input.setText(pw)
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))

    def save_password(self):
        site = self.site_input.text()
        username = self.username_input.text()
        password = self.password_input.text()
        if not site or not username or not password:
            QMessageBox.warning(self, "Error", "All fields are required")
            return
        enc_pw = encrypt(password, self.key)
        db = DatabaseManager()
        if self.edit_mode:
            db.update_password(self.pw_id, site, username, enc_pw)
        else:
            db.insert_password(self.user_id, site, username, enc_pw)
        db.close()
        self.accept()