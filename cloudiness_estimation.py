#!/usr/bin/env python3

import sys
import os
import configparser    
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


        
        self.values = self.get_values()
        print(self.values)
        #return#open("internals/config/camera.txt").read().splitlines()

        #FOV part
        lbl1 = QLabel("Width of View:", self)
        lbl1.move(20, 55)

        lbl2 = QLabel("Deg.", self)
        lbl2.move(140, 30)

        self.p1 = QLineEdit(self)
        self.p1.move(135, 50)
        self.p1.resize(45,30)
        self.p1.setText(self.values[0])

        #CVP part
        lbl3 = QLabel("Center of View:", self)
        lbl3.move(20, 120)

        lbl4 = QLabel("Az.", self)
        lbl4.move(140, 95)

        self.p2 = QLineEdit(self)
        self.p2.move(135, 115)
        self.p2.resize(45,30)
        self.p2.setText(self.values[1])

        lbl5 = QLabel("Ev.", self)
        lbl5.move(200, 95)

        self.p3 = QLineEdit(self)
        self.p3.move(190, 115)
        self.p3.resize(45,30)
        self.p3.setText(self.values[2])

        #ROT part
        lbl6 = QLabel("Camera Rotation:", self)
        lbl6.move(20, 185)

        lbl7 = QLabel("Deg.", self)
        lbl7.move(140, 160)

        self.p4 = QLineEdit(self)
        self.p4.move(135, 180)
        self.p4.resize(45,30)
        self.p4.setText(self.values[3])

        OK = QPushButton('OK', self)
        OK.resize(150, 50)
        OK.move(50, 250)
        OK.clicked.connect(self.ok_button)


    def get_values(self):
        camera_config = configparser.ConfigParser()
        camera_config.read("config.ini")
        wov = camera_config.get('CAMERA_VALUES','width_of_view')
        az = camera_config.get('CAMERA_VALUES','azimuth')
        h = camera_config.get('CAMERA_VALUES','elevation')
        rot = camera_config.get('CAMERA_VALUES','rotation')
        
        values = [wov, az, h, rot]
        return values

    def ok_button(self):

        wov = self.p1.text()
        az = self.p2.text()
        h = self.p3.text()
        rot = self.p4.text()

        wov_msg = ""
        if self.check_wov(wov) == False: wov_msg = "Width of View must have a value between 0-360.\n"

        az_msg = ""
        if self.check_az(az) == False: az_msg = "Azimuth must have a value between 0-180.\n"

        h_msg = ""
        if self.check_h(h) == False: h_msg = "Height must have a value between 0-90.\n"

        rot_msg = ""
        if self.check_rot(rot) == False: rot_msg = "Height must have a value between 0-90.\n"

        if self.check_input(wov, az, h, rot) == False:
            error = wov_msg + az_msg + h_msg + rot_msg
            QMessageBox.warning(self, "Input error", error, QMessageBox.Cancel)

        else:
            config_camera = configparser.ConfigParser()
            config_camera.read("config.ini")
            config_camera.set('CAMERA_VALUES', 'width_of_view', wov)
            config_camera.set('CAMERA_VALUES', 'azimuth', az)
            config_camera.set('CAMERA_VALUES', 'elevation', h)
            config_camera.set('CAMERA_VALUES', 'rotation', rot)
            
            with open('config.ini', 'w') as configfile:
                config_camera.write(configfile)            
            self.close()

    def is_number(self,s):
            try:
                float(s)
                return True
            except ValueError:
                return False

    def check_input(self, wov, az, h, rot):
        return (self.check_wov(wov) and self.check_az(az) and self.check_h(h) and self.check_rot(rot))

    def check_wov(self, wov):
        check = []
        for i in range (0, 361):
                check.append(str(i))
        if wov in check: return True
        else: return False

    def check_az(self, az):
        check = []
        for i in range (0, 181):
                check.append(str(i))
        if az in check: return True
        else: return False

    def check_h(self, h):
        check = []
        for i in range (0, 91):
                check.append(str(i))
        if h in check: return True
        else: return False

    def check_rot(self, rot):
        check = []
        for i in range (0, 91):
                check.append(str(i))
        if rot in check: return True
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
        OK.clicked.connect(self.ok_button)

        Cancel = QPushButton('Cancel', self)
        Cancel.resize(150, 50)
        Cancel.move (250, 110)
        Cancel.clicked.connect(self.cancel_button)

    def cancel_button(self):
        self.close()

    def ok_button(self):
        config_browse = configparser.ConfigParser()
        config_browse.read("config.ini")
        config_browse.set('BROWSE_PATH', 'browse_path', self.path)
        with open('config.ini', 'w') as configfile:
                config_browse.write(configfile)   
        """       
        f = open("internals/config/browse.txt", "w")
        f.write(self.path)
        f.close()
        """
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
        init = self.read_interval()
        self.interval.setText(init)

        #Checkbox init
        self.show_img = QCheckBox('Show images', self)
        self.show_img.move(220, 240)
        self.show_img.toggle()

        #Button init
        calc = QPushButton('Calculate', self)
        calc.resize(150, 50)
        calc.move(95, self.height-100)
        calc.clicked.connect(self.calculate_button)

        self.show()

    def read_interval(self):
        config_interval = configparser.ConfigParser()
        config_interval.read("config.ini")
        interval = config_interval.get('MAIN_VALUES', 'interval')
        return interval

    def camera(self):
        self.camera = CameraWindow()
        self.camera.show()

    def browse(self):
        self.B = BrowseWindow()
        self.B.show()

    def show_image(self):
        if self.show_img.isChecked():
            return True
            
        else:
            return False

    def calculate_button(self):
        if self.check_hm() == False:
            error = "Hours must have values between 0-23.\nMinutes must have values between 0-59."
            QMessageBox.warning(self, "Input error", error, QMessageBox.Cancel)
        if self.check_interval() == False:
            error = "Interval must be a number."
            QMessageBox.warning(self, "Input error", error, QMessageBox.Cancel)
        else:
            if self.check_ymd() == False:
                    error = "Start date must be older than End date."
                    QMessageBox.warning(self, "Input error", error, QMessageBox.Cancel)
            else:   
                                
                config = self.read_config()
                
                start_date = config[0]
                end_date = config[1]
                center_of_view = config[2]
                width_of_view = config[3]
                rotation = config[4]
                images_dir = config[5]
                interval = timedelta(minutes = int(config[6]))
                display_images = self.show_image()
                                                               
                cloudiness_perc = get_cloudiness_percentages(start_date, end_date, center_of_view, width_of_view, rotation, images_dir, interval, display_images)
                
                self.store_interval()
                self.store_dates()

                self.make_csv(cloudiness_perc)

                QMessageBox.information(self, "Success!", "Estimation was successful!", QMessageBox.Ok)

    def store_dates(self):

        start = str(self.d1.currentText()) + str(self.m1.currentText()) + str(self.y1.currentText()) + self.hour1.text() + self.min1.text()
        config_dates = configparser.ConfigParser()
        config_dates.read("config.ini")

        end = str(self.d2.currentText()) + str(self.m2.currentText()) + str(self.y2.currentText()) + self.hour2.text() + self.min2.text()
        
        config_dates.set('MAIN_VALUES', 'start_date', start)
        config_dates.set('MAIN_VALUES', 'end_date', end)
        with open('config.ini', 'w') as configfile:
            config_dates.write(configfile)

    def make_csv(self, cloudiness_perc):

        code = cloudiness_perc[0][0]
        mypath = "Tables"

        if not os.path.isdir(mypath):
           os.makedirs(mypath)

        file_path = "Tables/"+code+".csv"
        f = open(file_path, "w")
        f.write("time,cloudiness"+'\n')
        for info in cloudiness_perc:
            data = str(info[0]) + "," + (info[1]) + '\n'
            f.write(data)
        f.close()

    def is_number(self,s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    def check_hm(self):
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

    def check_ymd(self):
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

    def read_config(self):
        config = configparser.ConfigParser()
        config.read("config.ini")

        wov_config = int(config.get('CAMERA_VALUES', 'width_of_view'))
        azimuth_config = int(config.get('CAMERA_VALUES', 'azimuth'))
        height_config = int(config.get('CAMERA_VALUES', 'elevation'))
        rotation_config = int(config.get('CAMERA_VALUES', 'rotation'))
        
        start = config.get('MAIN_VALUES', 'start_date')
        start_config = datetime.strptime(start, "%d%m%Y%H%M")

        
        end = config.get('MAIN_VALUES', 'end_date')
        end_config = datetime.strptime(end, "%d%m%Y%H%M")
        
        browse_config  = config.get('MAIN_VALUES', 'interval')

        interval_config = config.get('BROWSE_PATH', 'browse_path')

        config = [start_config, end_config, (azimuth_config, height_config), wov_config,  rotation_config, interval_config, browse_config]
        
        return config
    
    def check_interval(self):
        return self.is_number(self.interval.text())

    def store_interval(self):
            
        config_interval = configparser.ConfigParser()
        config_interval.read("config.ini")
        config_interval.set('MAIN_VALUES', 'interval', self.interval.text())
        with open('config.ini', 'w') as configfile:
            config_interval.write(configfile)
        """
        f = open("internals/config/interval.txt", "w")
        f.write(self.interval.text())
        f.close
        """
    def close_event(self, event):

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
