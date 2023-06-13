# This is a sample Python script.
import sys
import PyQt5

from PyQt5.QtWidgets import QApplication

from loginWindow import LoginForm

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# Press the green button in the gutter to run the script.

if __name__ == '__main__':
    app = QApplication(sys.argv)
    width = app.desktop().screenGeometry().width()
    height = app.desktop().screenGeometry().height()
    form = LoginForm(width,height)
    form.show()

    sys.exit(app.exec_())
