#!/usr/bin/env python3

import sys
import os
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from datetime import *
from internals.cloud_detection import get_cloudiness_percentages

class CameraWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 250, 350)
        self.setWindowTitle('Field of View')
        self.setFixedSize(self.size())

        self.values = open("internals/config/camera.txt").read().splitlines()

        #FOV part
        self.lbl1 = QLabel("Width of View:", self)
        self.lbl1.move(20, 55)

        self.lbl2 = QLabel("Deg.", self)
        self.lbl2.move(140, 30)

        self.p1 = QLineEdit(self)
        self.p1.move(135, 50)
        self.p1.resize(45,30)
        self.p1.setText(self.values[0])

        #CVP part
        self.lbl3 = QLabel("Center of View:", self)
        self.lbl3.move(20, 120)

        self.lbl4 = QLabel("Az.", self)
        self.lbl4.move(140, 95)

        self.p2 = QLineEdit(self)
        self.p2.move(135, 115)
        self.p2.resize(45,30)
        self.p2.setText(self.values[1])


        self.lbl5 = QLabel("Ev.", self)
        self.lbl5.move(200, 95)

        self.p3 = QLineEdit(self)
        self.p3.move(190, 115)
        self.p3.resize(45,30)
        self.p3.setText(self.values[2])

        #ROT part
        self.lbl3 = QLabel("Camera Rotation:", self)
        self.lbl3.move(20, 185)


        self.lbl6 = QLabel("Deg.", self)
        self.lbl6.move(140, 160)

        self.p4 = QLineEdit(self)
        self.p4.move(135, 180)
        self.p4.resize(45,30)
        self.p4.setText(self.values[3])

        OK = QPushButton('OK', self)
        OK.resize(150, 50)
        OK.move(50, 250)
        OK.clicked.connect(self.okButton)

    def okButton(self):

        self.WoV = self.p1.text()
        self.Az = self.p2.text()
        self.H = self.p3.text()
        self.Rot = self.p4.text()

        self.WoV_msg = ""
        if self.checkWoV() == False: self.WoV_msg = "Width of View must have a value between 0-180.\n"

        self.Az_msg = ""
        if self.checkAz() == False: self.Az_msg = "Azimuth must have a value between 0-360.\n"

        self.H_msg = ""
        if self.checkH() == False: self.H_msg = "Height must have a value between 0-90.\n"

        self.Rot_msg = ""
        if self.checkRot() == False: self.Rot_msg = "Height must have a value between 0-90.\n"


        if self.checkInput() == False:
                error = self.WoV_msg + self.Az_msg + self.H_msg + self.Rot_msg
                QMessageBox.warning(self, "Input error", error, QMessageBox.Cancel)

        else:
                f = open("internals/config/camera.txt", "w")
                data = [self.WoV, self.Az, self.H, self.Rot]
                for p in data:
                        f.write(p+os.linesep)

                f.close()
                self.close()

    def is_number(self,s):
            try:
                float(s)
                return True
            except ValueError:
                return False

    def checkInput(self):
        return (self.checkWoV() and self.checkAz() and self.checkH() and self.checkRot())

    def checkWoV(self):
        check = []
        for i in range (0, 361):
                check.append(str(i))
        if self.WoV in check: return True
        else: return False

    def checkAz(self):
        check = []
        for i in range (0, 181):
                check.append(str(i))
        if self.Az in check: return True
        else: return False

    def checkH(self):
        check = []
        for i in range (0, 91):
                check.append(str(i))
        if self.H in check: return True
        else: return False

    def checkRot(self):
        check = []
        for i in range (0, 91):
                check.append(str(i))
        if self.Rot in check: return True
        else: return False

class BrowseWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 450, 200)
        self.setWindowTitle('Browse')
        self.setFixedSize(self.size())
        self.path = str(QFileDialog.getExistingDirectory())

        self.lbl0 = QLabel("Current Path: "+ self.path, self)
        self.lbl0.move(50, 20)


        self.lbl1 = QLabel("Save current path?", self)
        self.lbl1.move(160, 70)


        OK = QPushButton('OK', self)
        OK.resize(150, 50)
        OK.move(50, 110)
        OK.clicked.connect(self.okButton)

        Cancel = QPushButton('Cancel', self)
        Cancel.resize(150, 50)
        Cancel.move (250, 110)
        Cancel.clicked.connect(self.cancelButton)

    def cancelButton(self):
        self.close()

    def okButton(self):
        f = open("internals/config/browse.txt", "w")
        f.write(self.path)
        f.close()
        self.close()


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.initUI()


    def initUI(self):


        #toolbar init
        CameraAct = QAction(QIcon('internals/icons/fov.png'), 'Field of View', self)
        CameraAct.setShortcut('Ctrl+F')
        CameraAct.triggered.connect(self.camera)

        BrowseAct = QAction(QIcon('internals/icons/browse.png'), 'Browse for folder', self)
        BrowseAct.setShortcut('Ctrl+B')
        BrowseAct.triggered.connect(self.browse)

        self.toolbar = self.addToolBar('Field of View')
        self.toolbar.addAction(CameraAct)

        self.toolbar = self.addToolBar('Browse')
        self.toolbar.addAction(BrowseAct)

        #window init
        self.width = 340
        self.height = 400
        self.setGeometry(300, 300, self.width, self.height)
        self.setFixedSize(self.size())
        self.setWindowTitle('PMG camera')
        self.setWindowIcon(QIcon("fov.png"))
        self.center()


        #date1 input init

        self.lbl1 = QLabel("Start Time:", self)
        self.lbl1.move(70, 40)
        self.d1 = QComboBox(self)
        for day in range (1, 32):
                if day < 10:
                        date = "0" + str(day)
                else: date = str(day)
                self.d1.addItem(str(date))
        self.d1.resize(50, 30)
        self.d1.move(20, 70)

        self.m1 = QComboBox(self)
        for month in range (1, 13):
                if month < 10:
                        date = "0" + str(month)
                else: date = str(month)
                self.m1.addItem(date)
        self.m1.resize(50, 30)
        self.m1.move(70, 70)

        self.y1 = QComboBox(self)
        for year in range (2000, 2051):
                self.y1.addItem(str(year))
        self.y1.resize(70, 30)
        self.y1.move(120, 70)


        self.lbl2 = QLabel("Hrs.", self)
        self.lbl2.move(250, 40)
        self.hour1 = QLineEdit(self)
        self.hour1.move(250, 70)
        self.hour1.resize(30,30)
        self.hour1.setText("00")

        self.lbl3 = QLabel("Mins.", self)
        self.lbl3.move(290, 40)
        self.min1 = QLineEdit(self)
        self.min1.move(290, 70)
        self.min1.resize(30,30)
        self.min1.setText("00")


        #date 2 input init
        move_down = 80

        self.lbl4 = QLabel("End Time:", self)
        self.lbl4.move(70, 120)
        self.d2 = QComboBox(self)
        for day in range (1, 32):
                if day < 10:
                        date = "0" + str(day)
                else: date = str(day)
                self.d2.addItem(str(date))
        self.d2.resize(50, 30)
        self.d2.move(20, 70+move_down)

        self.m2 = QComboBox(self)
        for month in range (1, 13):
                if month < 10:
                        date = "0" + str(month)
                else: date = str(month)
                self.m2.addItem(date)
        self.m2.resize(50, 30)
        self.m2.move(70, 70+move_down)

        self.y2 = QComboBox(self)
        for year in range (2000, 2051):
                self.y2.addItem(str(year))
        self.y2.resize(70, 30)
        self.y2.move(120, 70+move_down)


        self.lbl5 = QLabel("Hrs.", self)
        self.lbl5.move(250, 120)
        self.hour2 = QLineEdit(self)
        self.hour2.resize(30,30)
        self.hour2.move(250, 70+move_down)
        self.hour2.setText("00")

        self.lbl5 = QLabel("Mins.", self)
        self.lbl5.move(290, 120)
        self.min2 = QLineEdit(self)
        self.min2.resize(30,30)
        self.min2.move(290, 70+move_down)
        self.min2.setText("00")
        #Interval init

        self.lbl6 = QLabel("Interval:", self)
        self.lbl6.move(20, 240)
        self.interval = QLineEdit(self)
        self.interval.resize(40, 30)
        self.interval.move(80, 240)
        self.lbl6 = QLabel("Mins.", self)
        self.lbl6.move(82, 210)
        init = open("internals/config/interval.txt", "r").read().splitlines()
        self.interval.setText(init[0])

        #Checkbox init
        self.show_image = QCheckBox('Show images', self)
        self.show_image.move(220, 240)
        self.show_image.toggle()
        self.show_image.stateChanged.connect(self.showImage)

        #Button init

        calc = QPushButton('Calculate', self)
        calc.resize(150, 50)
        calc.move(95, self.height-100)
        calc.clicked.connect(self.calculateButton)

        self.show()


    def camera(self):
        self.camera = CameraWindow()
        self.camera.show()

    def browse(self):
        self.B = BrowseWindow()
        self.B.show()

    def showImage(self, state):
        if state == Qt.Checked:
            self.show_config = True
        else:
            self.show_config = False


    def calculateButton(self):
        if self.checkHM() == False:
                error = "Hours must have values between 0-23.\nMinutes must have values between 0-59."
                QMessageBox.warning(self, "Input error", error, QMessageBox.Cancel)
        if self.checkInterval() == False:
                error = "Interval must be a number."
                QMessageBox.warning(self, "Input error", error, QMessageBox.Cancel)
        else:
                if self.checkYMD() == False:
                        error = "Start date must be older than End date."
                        QMessageBox.warning(self, "Input error", error, QMessageBox.Cancel)
                else:   
                        self.storeInterval()
                        self.storeDates()
                        
                        self.readConfig()
                        start_date = self.begin_config
                        end_date = self.end_config
                        center_of_view = (self.azimuth_config, self.height_config)
                        width_of_view = self.WoV_config
                        rotation = self.rotation_config
                        images_dir = self.browse_config
                        interval = timedelta(minutes = self.interval_config)

                        display_images = True#self.show_config
                        
                        self.Banjo = get_cloudiness_percentages(start_date, end_date, center_of_view, width_of_view, rotation, images_dir, interval, display_images)
                        
                        self.makeCSV()

                        #use WoV, azimuth, height, rotation, begin, end, interval, show and browse with prefix self. and sifux _config

                        QMessageBox.information(self, "Success!", "Estimation was successful!", QMessageBox.Ok)

    def storeDates(self):

        begin = str(self.d1.currentText()) + str(self.m1.currentText()) + str(self.y1.currentText()) + self.hour1.text() + self.min1.text()

        fbegin = open("internals/config/begin.txt", "w")
        fbegin.write(begin)
        fbegin.close()

        end = str(self.d2.currentText()) + str(self.m2.currentText()) + str(self.y2.currentText()) + self.hour2.text() + self.min2.text()

        fend = open("internals/config/end.txt", "w")
        fend.write(end)
        fend.close()

    def makeCSV(self):

        code = self.Banjo[0][0]
        file_path = "tables/"+code+".csv"
        f = open(file_path, "w")
        f.write("time,cloudiness"+'\n')
        for info in self.Banjo:
                        data = str(info[0]) + "," + (info[1]) + '\n'
                        f.write(data)
        f.close()

    def is_number(self,s):
            try:
                int(s)
                return True
            except ValueError:
                return False

    def checkHM(self):
        check = True

        h1 = self.hour1.text()
        h2 = self.hour2.text()

        m1 = self.min1.text()
        m2 = self.min2.text()

        if (m1 == "00"): m1 = "0"
        if (m2 == "00"): m2 = "0"

        if (h1 == "00"): h1 = "0"
        if (h2 == "00"): h2 = "0"

        if(len(m1) == 2) and(m1[0] == "0"): m1 = m1[1]
        if(len(m2) == 2) and(m2[0] == "0"): m2 = m2[1]

        hours = []
        for i in range(0, 24):
                hours.append(str(i))

        mins = []
        for i in range(0, 60):
                mins.append(str(i))

        if (h1 in hours) and (h2 in hours):
                check = True
        else:
                check = False
                return check

        if (m1 in mins) and (m2 in mins):
                check = True
        else:
                check = False
                return check



    def checkYMD(self):
        check = True

        year1 = self.y1.currentText()
        year2 = self.y2.currentText()

        month1 = self.m1.currentText()
        month2 = self.m2.currentText()

        day1 = self.d1.currentText()
        day2 = self.d2.currentText()

        hour1 = self.hour1.text()
        hour2 = self.hour2.text()

        min1 = self.min1.text()
        min2 = self.min2.text()

        if (len(hour1)==1): hour1 = "0" + hour1
        if (len(hour2)==1): hour2 = "0" + hour2

        start = day1 + month1 + year1 + hour1 + min1
        end = day2 + month2 + year2 + hour2 + min2

        date_start = datetime.strptime(start, "%d%m%Y%H%M")
        date_end = datetime.strptime(end, "%d%m%Y%H%M")

        if(date_start < date_end): return check
        else:
                 check = False
                 return check

    def readConfig(self):
        camera = open("internals/config/camera.txt", "r").read().splitlines()
        self.WoV_config = int(camera[0])
        self.azimuth_config = int(camera[1])
        self.height_config = int(camera[2])
        self.rotation_config = int(camera[3])

        f = open("internals/config/begin.txt", "r").read().splitlines()
        begin = f[0]
        self.begin_config = datetime.strptime(begin, "%d%m%Y%H%M")

        f = open("internals/config/end.txt", "r").read().splitlines()
        end = f[0]
        self.end_config = datetime.strptime(end, "%d%m%Y%H%M")

        f = open("internals/config/interval.txt", "r").read().splitlines()
        self.interval_config = int(f[0])

        f = open("internals/config/browse.txt", "r").read().splitlines()
        self.browse_config  = f[0]



    def checkInterval(self):
        return self.is_number(self.interval.text())

    def storeInterval(self):
        f = open("internals/config/interval.txt", "w")
        f.write(self.interval.text())
        f.close

    def closeEvent(self, event):

        reply = QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QMessageBox.No |
            QMessageBox.Yes, QMessageBox.Yes)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def center(self):

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
