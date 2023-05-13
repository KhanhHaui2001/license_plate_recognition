import sys
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog
from PyQt5 import QtWidgets

class fDialog(QDialog):

    def __init__(self):
        super(fDialog, self).__init__()
        loadUi('dialog.ui',self)
        self.ref=None