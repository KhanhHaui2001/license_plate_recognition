import sys
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog
from PyQt5 import QtWidgets

class fMessage(QDialog):

    def __init__(self):
        super(fMessage, self).__init__()
        loadUi('message.ui',self)
        self.ref=None