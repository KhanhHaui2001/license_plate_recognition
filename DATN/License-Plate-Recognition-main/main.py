from datetime import datetime
import sys
from threading import activeCount
from turtle import clear
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QLabel, QDialog, QTableWidgetItem, QApplication, QMainWindow, QTableWidget, QFileDialog
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QPixmap
import torch  
from dialog import fDialog
from image import fImage
from message import fMessage
from error import fError
from history import fHistory
# from register import fRegister
from mysql.connector import (connection)
import os
import function.helper as helper
import function.utils_rotate as utils_rotate
import time
import cv2
from PIL import Image
import numpy as np
import tensorflow as tf
import keras

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
userDB='root'
passwordDB='0835892056'
hostDB='localhost'
databaseDB='number_plate_recognition'


dir = 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/'

#nạp giao diện
Ui_MainWindow, QtBaseClass = uic.loadUiType('login.ui')

class frmMain(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.btnLogin.clicked.connect(self.login)
        self.registerBtn.clicked.connect(self.register)

    def login(self):
        try: 
            username = fMain.lineEditUsername.text()
            password = fMain.lineEditPassword.text()
            if username == '':
                fMain.userError.setText('Tên đăng nhập là bắt buộc')
            else: 
                fMain.userError.setText('')
            if password == '':
                fMain.passError.setText('Mật khẩu là bắt buộc')
            else:
                fMain.passError.setText('')
            if username != '' and password != '':
                mydb = connection.MySQLConnection(user=userDB, password=passwordDB,
                                    host=hostDB,
                                    database=databaseDB)
                mycursor = mydb.cursor()
                sql = "SELECT * FROM user WHERE username = '" + username + "' AND password = md5('" + password + "')"
                mycursor.execute(sql)

                myresult = mycursor.fetchone()
                if myresult == None:
                    fDialog.show()
                else:
                    self.w = fRecognition.show()
                    self.hide()
                mydb.close()
        except connection.Error as e:
            fError.show()

    def register(self):
        self.w = fRegister.show()
        fMain.lineEditUsername.setText('')
        fMain.lineEditPassword.setText('')
        fMain.userError.setText('')
        fMain.passError.setText('')
        self.hide()

class fRecognition(QtWidgets.QMainWindow):
    
    def __init__(self):
      super(fRecognition, self).__init__()
      loadUi('lp_detection.ui', self)
      self.ref=None
      self.chooseFileBtn.clicked.connect(self.openFileDialog)
      self.historyBtn.clicked.connect(self.openHistoryForm)
      self.logoutBtn.clicked.connect(self.logout)
      self.turnOnCam.clicked.connect(self.realTime)

    def openFileDialog(self):
      fname, _ = QFileDialog.getOpenFileName(self, 'Open file', 
        'c:\\',"Image files (*.jpg *.gif *.jpeg *.png)")
      if fname != "":
        self.image.setPixmap(QPixmap(fname))
        # show the image
        number_plate_recog(fname)
        # keep the window open until we press a key
        cv2.waitKey(0)
        # close the window
        cv2.destroyAllWindows()
      else:
        fImage.show()
    
    def openHistoryForm(self):
      self.image.clear()
      self.w = fHistory.show()
      self.hide()
      cv2.destroyAllWindows()

    def realTime(self):
        yolo_LP_detect = torch.hub.load('yolov5', 'custom', path='model/LP_detector_nano_61.pt', force_reload=True, source='local')
        yolo_license_plate = torch.hub.load('yolov5', 'custom', path='model/LP_ocr_nano_62.pt', force_reload=True, source='local')
        yolo_license_plate.conf = 0.60

        prev_frame_time = 0
        new_frame_time = 0

        vid = cv2.VideoCapture(0)
        
        mydb = connection.MySQLConnection(user=userDB, password=passwordDB,
                                    host=hostDB,
                                    database=databaseDB)
        while(True):
            ret, frame = vid.read()
            
            plates = yolo_LP_detect(frame, size=640)
            list_plates = plates.pandas().xyxy[0].values.tolist()
            list_read_plates = set()
            for plate in list_plates:
                flag = 0
                x = int(plate[0]) # xmin
                y = int(plate[1]) # ymin
                w = int(plate[2] - plate[0]) # xmax - xmin
                h = int(plate[3] - plate[1]) # ymax - ymin  
                crop_img = frame[y:y+h, x:x+w]
                cv2.rectangle(frame, (int(plate[0]),int(plate[1])), (int(plate[2]),int(plate[3])), color = (0,0,225), thickness = 2)
                cv2.imwrite("crop.jpg", crop_img)
                rc_image = cv2.imread("crop.jpg")
                lp = ""
                for cc in range(0,2):
                    for ct in range(0,2):
                        lp = helper.read_plate(yolo_license_plate, utils_rotate.deskew(crop_img, cc, ct))
                        if lp != "unknown":
                            list_read_plates.add(lp)
                            cv2.putText(frame, lp, (int(plate[0]), int(plate[1]-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
                            flag = 1
                            break
                    if flag == 1:
                        break
            new_frame_time = time.time()
            fps = 1/(new_frame_time-prev_frame_time)
            prev_frame_time = new_frame_time
            fps = int(fps)
            cv2.putText(frame, str(fps), (7, 70), cv2.FONT_HERSHEY_SIMPLEX, 3, (100, 255, 0), 3, cv2.LINE_AA)
            cv2.imshow('Output', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            img_name = datetime.today().strftime('%Y_%m_%d_%H_%M_%S') + ".jpg"
            img_path = os.path.join(dir , img_name)
            mycursor = mydb.cursor()
            if list_read_plates:
                cv2.imwrite(img_path, frame)
                sql = "INSERT INTO event(plate, image) VALUES ('" + ', '.join(list_read_plates) + "', LOAD_FILE('" + img_path + "'))"
                mycursor.execute(sql)
            mydb.commit()
        mydb.close()

        vid.release()
        cv2.destroyAllWindows()

    def logout(self):
        self.close()
        fMain.lineEditUsername.setText('')
        fMain.lineEditPassword.setText('')
        self.image.clear()
        fMain.show()

class fRegister(QtWidgets.QMainWindow):
    def __init__(self):
      super(fRegister, self).__init__()
      loadUi('register.ui', self)
      self.ref=None
      self.registerBtn.clicked.connect(self.register)
      self.cancelBtn.clicked.connect(self.cancel)

    def register(self):
        try: 
            username = self.lineEditUsername.text()
            password = self.lineEditPassword.text()
            if username == '':
                self.userError.setText('Tên đăng nhập là bắt buộc')
            else: 
                self.userError.setText('')
            if password == '':
                self.passError.setText('Mật khẩu là bắt buộc')
            else:
                self.passError.setText('')
            if username != '' and password != '':
                mydb = connection.MySQLConnection(user=userDB, password=passwordDB,
                                    host=hostDB,
                                    database=databaseDB)
                mycursor = mydb.cursor()
                sql = "SELECT * FROM user WHERE username = '" + username + "'"
                mycursor.execute(sql)
                if(mycursor.fetchone() == None):
                    sql = "INSERT INTO user(username, password) VALUES ('" + username + "', MD5('" + password + "'))"
                    mycursor.execute(sql)
                    mydb.commit()
                    myresult = mycursor.lastrowid
                    if myresult == None:
                        print('sai roi')
                    else:
                        clearData()
                        fRecognition.show()
                        self.close()
                else:
                    fMessage.show()
                
                mydb.close()
        except connection.Error as e:
            fError.show()

    def cancel(self):
        clearData()
        fMain.show()
        self.close()

class fHistory(QtWidgets.QMainWindow):
    def __init__(self):
      super(fHistory, self).__init__()
      loadUi('history.ui', self)
      self.ref=None
      self.recognitionBtn.clicked.connect(self.recognition)
      self.readBtn.clicked.connect(self.showData)
      self.logoutBtn.clicked.connect(self.logout)
    
    def showData(self):
      self.tableWidget.setRowCount(0)
      mydb = connection.MySQLConnection(user=userDB, password=passwordDB,
                                    host=hostDB,
                                    database=databaseDB)
      mycursor = mydb.cursor()
      sql = "SELECT created_date, plate, image  FROM event order by created_date desc LIMIT 50"
      mycursor.execute(sql)
      result = mycursor.fetchall()
      for row_number, row_data in enumerate(result):
        self.tableWidget.insertRow(row_number)
        for column_number, column_data in enumerate(row_data):
            if isinstance(column_data, datetime):
                column_data = datetime.strftime(column_data, "%d/%m/%Y %H:%M:%S")
            item = str(column_data)
            if(column_number == 2):
                item = self.getImageLabel(column_data)
                self.tableWidget.setCellWidget(row_number,column_number,item)
                
            else: 
                self.tableWidget.setItem(row_number,column_number,QtWidgets.QTableWidgetItem(item))
      self.tableWidget.verticalHeader().setDefaultSectionSize(80)
      mydb.close()

    def getImageLabel(self,image):
        imageLabel = QtWidgets.QLabel(self.centralwidget)
        imageLabel.setText("")
        imageLabel.setScaledContents(True)
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(image,'jpg')
        imageLabel.setPixmap(pixmap)
        return imageLabel

    def recognition(self):
      self.tableWidget.setRowCount(0)
      self.w = fRecognition.show()
      self.hide()

    def logout(self):
        self.tableWidget.setRowCount(0)
        self.close()
        fMain.lineEditUsername.setText('')
        fMain.lineEditPassword.setText('')
        fMain.show()

def clearData():
    fRegister.lineEditUsername.setText('')
    fRegister.lineEditPassword.setText('')
    fRegister.userError.setText('')
    fRegister.passError.setText('')

def number_plate_recog(img_path):
    yolo_LP_detect = torch.hub.load('yolov5', 'custom', path='model/LP_detector.pt', force_reload=True, source='local')
    yolo_license_plate = torch.hub.load('yolov5', 'custom', path='model/LP_ocr.pt', force_reload=True, source='local')
    yolo_license_plate.conf = 0.60
    
    img = cv2.imread(img_path)
    plates = yolo_LP_detect(img, size=640)
    
    list_plates = plates.pandas().xyxy[0].values.tolist()
    list_read_plates = set()
    if len(list_plates) == 0:
        lp = helper.read_plate(yolo_license_plate,img)
        if lp != "unknown":
            cv2.putText(img, lp, (7, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
            list_read_plates.add(lp)
    else:   
        for plate in list_plates:
            flag = 0
            x = int(plate[0]) # xmin
            y = int(plate[1]) # ymin
            w = int(plate[2] - plate[0]) # xmax - xmin
            h = int(plate[3] - plate[1]) # ymax - ymin  
            crop_img = img[y:y+h, x:x+w]
            cv2.rectangle(img, (int(plate[0]),int(plate[1])), (int(plate[2]),int(plate[3])), color = (0,0,225), thickness = 2)
            cv2.imwrite("crop.jpg", crop_img)
            rc_image = cv2.imread("crop.jpg")
            lp = ""
            for cc in range(0,2):
                for ct in range(0,2):
                    lp = helper.read_plate(yolo_license_plate, utils_rotate.deskew(crop_img, cc, ct))
                    if lp != "unknown":
                        list_read_plates.add(lp)
                        cv2.putText(img, lp, (int(plate[0]), int(plate[1]-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
                        flag = 1
                        break
                if flag == 1:
                    break
                
    cv2.imshow('Output', img)
    img_name = datetime.today().strftime('%Y_%m_%d_%H_%M_%S') + ".jpg"
    img_path = os.path.join(dir , img_name)
    cv2.imwrite(img_path, img)
    
    mydb = connection.MySQLConnection(user=userDB, password=passwordDB,
                                host=hostDB,
                                database=databaseDB)
    mycursor = mydb.cursor()
    sql = "INSERT INTO event(plate, image) VALUES ('" + ', '.join(list_read_plates) + "', LOAD_FILE('" + img_path + "'))"
    mycursor.execute(sql)
    mydb.commit()
    mydb.close()
    cv2.waitKey()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    fMain = frmMain()
    fMain.show()

    fMessage = fMessage()
    fDialog = fDialog()
    fRegister = fRegister()
    fRecognition = fRecognition()
    fHistory = fHistory()
    fImage = fImage()
    fError = fError()
    sys.exit(app.exec_())