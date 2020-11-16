from PyQt5.QtCore import pyqtSignal, QThread, Qt , QTime, QTimer

class Timer(QThread):

    updateTimeText = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        
        

        timer = QTimer(self)
        timer.timeout.connect(self.updateTime)
        timer.start(1000)

        self.mins = 59
        self.secs = 59

    def updateTime(self):

        if self.secs == 0:
            self.mins -= 1
            self.secs = 59
        else:
            self.secs -= 1

        
        if self.mins < 10:
            mins = '0'+ str(self.mins)
        else:
            mins = str(self.mins)

        if self.secs < 10:
            secs = '0'+str(self.secs)
        else:
            secs = str(self.secs)

        time = mins + ' : ' + secs

        print(time)

c = Timer()
        
        




