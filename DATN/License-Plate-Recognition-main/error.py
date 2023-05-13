import sys
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog
from PyQt5 import QtWidgets

class fError(QDialog):

    def __init__(self):
        super(fError, self).__init__()
        loadUi('error.ui',self)
        self.ref=None