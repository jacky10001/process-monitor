
import os
import sys
import time
import psutil
from threading import Thread, Event
from Ui_interface import Ui_Form
from PyQt5 import QtCore, QtGui, QtWidgets


class MonitorThread(Thread):
    def __init__(self, view, process_pid):
        super(MonitorThread, self).__init__()
        self.view = view
        self.process_pid = process_pid
        self.interval = 60
        self.open = True
        self.daemon = True
        self.exit_event = Event()
        
    def run(self):
        while self.open:
            pids = psutil.pids()
            if self.process_pid in pids:
                print("PID is live !!!")
            else:
                print("Not found PID ...")
            if self.exit_event.wait(self.interval):
                break
        print()
    
    def stop(self):
        self.open = False



class MyApp(QtWidgets.QMainWindow, Ui_Form):    
    def __init__(self, parent=None):
        super(MyApp, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.btn_event.clicked.connect(self.onStart)

    def onStart(self):
        if self.lineEdit.text() == "":
            print("No pid ...")
            return
        if not self.lineEdit.text().isdigit():
            print("Error!! Please enter digit ...")
            return
        process_pid = int(self.lineEdit.text())
        self.monitor = MonitorThread(self, process_pid)
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