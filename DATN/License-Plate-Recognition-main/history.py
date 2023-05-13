import sys
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog
from PyQt5 import QtWidgets

class fHistory(QtWidgets.QMainWindow):

    def __init__(self):
        super(fHistory, self).__init__()
        loadUi('history.ui',self)
        self.ref=None