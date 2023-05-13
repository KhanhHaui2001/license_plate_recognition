# import sys
# import base64
# from threading import activeCount
# from turtle import clear
# from PyQt5 import QtCore, QtGui, QtWidgets, uic
# from PyQt5.uic import loadUi
# from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QApplication, QMainWindow, QTableWidget, QFileDialog
# from PyQt5 import QtWidgets, QtCore, QtGui
# from PyQt5.QtGui import QPixmap
# from dialog import fDialog
# from image import fImage
# from message import fMessage
# from error import fError
# # from register import fRegister
# from mysql.connector import (connection)
# import os

# from user_management import frmMain

# fMain = frmMain()

# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# import cv2
# from PIL import Image
# import numpy as np
# import tensorflow as tf
# import keras

# userDB='root'
# passwordDB='0835892056'
# hostDB='localhost'
# databaseDB='number_plate_recognition'

# class fRegister(QtWidgets.QMainWindow):
#     def __init__(self):
#       super(fRegister, self).__init__()
#       loadUi('register.ui', self)
#       self.ref=None
#       self.registerBtn.clicked.connect(self.register)
#       self.cancelBtn.clicked.connect(self.cancel)

#     def register(self):
#         try: 
#             username = self.lineEditUsername.text()
#             password = self.lineEditPassword.text()
#             if username == '':
#                 self.userError.setText('Tên đăng nhập là bắt buộc')
#             else: 
#                 self.userError.setText('')
#             if password == '':
#                 self.passError.setText('Mật khẩu là bắt buộc')
#             else:
#                 self.passError.setText('')
#             if username != '' and password != '':
#                 mydb = connection.MySQLConnection(user=userDB, password=passwordDB,
#                                     host=hostDB,
#                                     database=databaseDB)
#                 mycursor = mydb.cursor()
#                 sql = "SELECT * FROM user WHERE username = '" + username + "'"
#                 mycursor.execute(sql)
#                 if(mycursor.fetchone() == None):
#                     sql = "INSERT INTO user(username, password) VALUES ('" + username + "', MD5(' " + password + "'))"
#                     mycursor.execute(sql)
#                     mydb.commit()
#                     myresult = mycursor.lastrowid
#                     if myresult == None:
#                         print('sai roi')
#                     else:
#                         clearData()
#                         # fEmotion.show()
#                         self.close()
#                 else:
#                     fMessage.show()

#                 mydb.close()
#         except connection.Error as e:
#             fError.show()

#     def cancel(self):
#         clearData()
#         fMain.show()
#         self.close()
        
# def clearData():
#     fRegister.lineEditUsername.setText('')
#     fRegister.lineEditPassword.setText('')
#     fRegister.userError.setText('')
#     fRegister.passError.setText('')