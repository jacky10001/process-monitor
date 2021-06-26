
import os
import sys
import time
import psutil
import numpy as np
import pyqtgraph as pg
from pyqtgraph import PlotWidget
from threading import Thread
from Ui_interface import Ui_Form
from Ui_cron_ui import Ui_CRON
from PyQt5 import QtCore, QtGui, QtWidgets
import requests


class MonitorThread(Thread):
    def __init__(self, view, process_pid, token, interval):
        super(MonitorThread, self).__init__()
        self.view = view
        self.process_pid = process_pid
        self.interval = interval
        self.token = token
        self.open = True
        self.daemon = True
        self.lineNotifyMessage("監控程式啟動......")
        
    def run(self):
        count = 0
        self.open = True
        t1 = time.time()
        t2 = t1
        while self.open:
            pids = psutil.pids()
            if self.interval:
                next_time = self.interval - int(t2 - t1)
                self.view.next_time("Next sending time: %d sec"%(next_time))
                if t2-t1 > self.interval:
                    if self.process_pid in pids:
                        self.lineNotifyMessage("PID %d 執行中 !!!"%self.process_pid)
                    else:
                        self.lineNotifyMessage("找不到 PID %d ..."%self.process_pid)
                        self.stop()
                        self.view.reconnect_signal("start")
                        break
                    t1 = time.time()
                else:
                    t2 = time.time()
            else:
                self.view.next_time("No Alarm")
            if count%2 == 0:
                try:
                    proc = psutil.Process(self.process_pid)
                    cpu_percent = proc.cpu_percent()
                    mem_percent = proc.memory_percent()
                    self.view.notify(cpu_percent, mem_percent)
                except:
                    self.lineNotifyMessage("錯誤!! 程式已關閉......")
                    self.stop()
                    self.view.reconnect_signal("start")
                    break
            time.sleep(0.5)
            count += 1
        self.view.next_time("")
        self.lineNotifyMessage("監控程式已關閉......")
    
    def lineNotifyMessage(self, msg):
        print(msg)
        if self.token:
            headers = {
                "Authorization": "Bearer " + self.token,
                "Content-Type" : "application/x-www-form-urlencoded"
            }
            payload = {"message": msg }
            r = requests.post(
                "https://notify-api.line.me/api/notify",
                headers=headers, params=payload)
            return r.status_code
    
    def stop(self):
        self.open = False


class MyApp(QtWidgets.QMainWindow, Ui_Form):    
    def __init__(self, parent=None):
        super(MyApp, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.token = ""
        self.interval = 0
        self.monitor = None
        self.cron_ui = MyCron()
        self.btn_event.clicked.connect(self.onStart)
        self.btn_openCronUi.clicked.connect(self.openCronUi)
        self.cron_ui.update_cron_time.connect(self.set_cron_time)
        
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        # Add PlotWidget control
        self.plotWidget_ted = PlotWidget(self)
        # Set the size and relative position of the control
        self.plotWidget_ted.setGeometry(QtCore.QRect(20,250,351,181))
        self.data1 = np.zeros((100))

        self.curve1 = self.plotWidget_ted.plot(self.data1, name="mode1")
    
    def set_cron_time(self, interval):
        if not self.monitor:
            print("Set cron time")
            self.interval = interval
        else:
            print("Change cron time")
            self.monitor.interval = interval
    
    def next_time(self, msg):
        self.lbl_alarm.setText(msg)
    
    def notify(self, cpu_percent, mem_percent):
        current_time = time.strftime('%Y%m%d-%H%M%S',time.localtime(time.time()))
        line = "Time: {} CPU: {} Memory: {}".format(current_time, cpu_percent, mem_percent)
        print (line)
        self.data1[:-1] = self.data1[1:]
        self.data1[-1] = mem_percent
        self.curve1.setData(self.data1)

    def onStart(self):
        if self.lineEdit.text() == "":
            print("No pid ...")
            return
        if not self.lineEdit.text().isdigit():
            print("Error!! Please enter digit ...")
            return
        if not self.lineEdit_2.text():
            print("Warning!! Not enter token ...")
            print("Only print message to window ...")
        token = self.lineEdit_2.text()
        process_pid = int(self.lineEdit.text())
        interval = self.interval
        self.monitor = MonitorThread(self, process_pid, token, interval)
        self.monitor.start()
        self.reconnect_signal("stop")

    def onStop(self):
        self.monitor.stop()
        self.monitor.join(1)
        self.monitor = None
        self.reconnect_signal("start")

    def reconnect_signal(self, target):
        if target == "start":
            self.btn_event.clicked.connect(self.onStart)
            self.btn_event.clicked.disconnect(self.onStop)
        elif target == "stop":
            self.btn_event.clicked.disconnect(self.onStart)
            self.btn_event.clicked.connect(self.onStop)
        self.btn_event.setText(target)

    def closeEvent(self, event):
        self.close()

    def openCronUi(self):
        self.cron_ui.show()


class MyCron(QtWidgets.QMainWindow, Ui_CRON):
    update_cron_time = QtCore.pyqtSignal(float)

    def __init__(self, parent=None):
        super(MyCron, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.slider_m.valueChanged.connect(self.setSliderMinutes)
        self.slider_h.valueChanged.connect(self.setSliderHours)
        self.sb_m.valueChanged.connect(self.setSbMinutes)
        self.sb_h.valueChanged.connect(self.setSbHours)
        self.btn_reset.clicked.connect(self.onReset)
        self.btn_set.clicked.connect(self.onSet)

    def setSliderMinutes(self):
        self.sb_m.setValue(self.slider_m.value())

    def setSliderHours(self):
        self.sb_h.setValue(self.slider_h.value())

    def setSbMinutes(self):
        self.slider_m.setValue(self.sb_m.value())

    def setSbHours(self):
        self.slider_h.setValue(self.sb_h.value())

    def onReset(self):
        self.slider_m.setValue(0)
        self.slider_h.setValue(0)

    def onSet(self):
        hour, minute = self.sb_h.value(), self.sb_m.value()
        second = hour*3600 + minute*60
        print("Cron Time:", second, "sec", " ( Hours:", hour, " Miniutes:", minute, ")")
        self.update_cron_time.emit(second)
        self.close()


if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = MyApp()
    win.show()
    sys.exit(app.exec_())