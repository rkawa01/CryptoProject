import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QLineEdit, QGridLayout, QMessageBox)
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from getInfo import JsonInfo
import plotWindow


class LoginForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Login Form')
        self.resize(500, 120)

        layout = QGridLayout()

        label_name = QLabel('<font size="4"> Username </font>')
        self.lineEdit_username = QLineEdit()
        self.lineEdit_username.resize(150, 20)
        self.lineEdit_username.setPlaceholderText('Please enter your username')
        layout.addWidget(label_name, 0, 0)
        layout.addWidget(self.lineEdit_username, 0, 1)

        label_password = QLabel('<font size="4"> Password </font>')
        self.lineEdit_password = QLineEdit()
        self.lineEdit_password.setPlaceholderText('Please enter your password')
        layout.addWidget(label_password, 1, 0)
        layout.addWidget(self.lineEdit_password, 1, 1)

        button_login = QPushButton('Login')
        button_login.clicked.connect(self.check_password)
        layout.addWidget(button_login, 2, 0, 1, 2)
        layout.setRowMinimumHeight(2, 75)

        # error_label = QLabel('', self)
        self.error_label = QLabel("", self)
        layout.addWidget(self.error_label, 3, 0, 1, 2)
        self.error_label.setStyleSheet("QLabel { color : red; }")
        self.error_label.setAlignment(Qt.AlignCenter)
        # self.error_label.move(50, 180)
        # self.error_label.resize(300, 20)

        self.setLayout(layout)

    def check_password(self):

        msg = QMessageBox()
        object_json = JsonInfo(self.lineEdit_username.text(),self.lineEdit_password.text())
        object_json.postresponse()
        # print(object_json.info)
        if object_json.info["message"] is not None:
            self.hide()
            self.next_window = plotWindow.PlotWindow(request = object_json, username = self.lineEdit_username.text())
            self.next_window.show()
            msg.setText('Success')
            msg.exec_()

        else:
            # Show error message
            msg.setText('Incorrect username or password')
            msg.exec_()
            self.error_label.setText("Incorrect username or password")

