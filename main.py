
import os
import sys
import time
import psutil
import numpy as np
import pyqtgraph as pg
from pyqtgraph import PlotWidget
from threading import Thread
from Ui_interface import Ui_Form
from PyQt5 import QtCore, QtGui, QtWidgets
import requests


class MonitorThread(Thread):
    def __init__(self, view, process_pid, token):
        super(MonitorThread, self).__init__()
        self.view = view
        self.process_pid = process_pid
        self.interval = 300
        self.open = True
        self.daemon = True
        self.token = token
        self.lineNotifyMessage("監控程式啟動......")
        
    def run(self):
        count = 0
        while self.open:
            pids = psutil.pids()
            if count%self.interval == 0:
                if self.process_pid in pids:
                    self.lineNotifyMessage("PID %d 執行中 !!!"%self.process_pid)
                else:
                    self.lineNotifyMessage("找不到 PID %d ..."%self.process_pid)
                    break
            if count%2 == 0:
                try:
                    proc = psutil.Process(self.process_pid)
                    cpu_percent = proc.cpu_percent()
                    mem_percent = proc.memory_percent()
                    self.view.notify(cpu_percent, mem_percent)
                except:
                    self.lineNotifyMessage("錯誤!! 程式已關閉......")
                    break
            time.sleep(0.5)
            count += 1
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
        self.btn_event.clicked.connect(self.onStart)
        self.token = ""

        
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        # Add PlotWidget control
        self.plotWidget_ted = PlotWidget(self)
        # Set the size and relative position of the control
        self.plotWidget_ted.setGeometry(QtCore.QRect(20,230,351,181))
        self.data1 = np.zeros((100))

        self.curve1 = self.plotWidget_ted.plot(self.data1, name="mode1")
    
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
        self.monitor = MonitorThread(self, process_pid, token)
        self.monitor.start()
        self.reconnect_signal("stop")

    def onStop(self):
        self.monitor.stop()
        self.monitor.join(1)
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


if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = MyApp()
    win.show()
    sys.exit(app.exec_())