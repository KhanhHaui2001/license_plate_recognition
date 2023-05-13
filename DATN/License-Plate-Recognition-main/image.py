import sys
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog
from PyQt5 import QtWidgets

class fImage(QDialog):

    def __init__(self):
        super(fImage, self).__init__()
        loadUi('image.ui',self)
        self.ref=None