import cv2
import numpy
import sys
import time
import mainwindow


from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow
from PyQt5.uic  import loadUi
from video      import video_sequence_by1, video_sequence_byn

################################################################################
#class Main(QMainWindow, Ui_MainWindow):
class Main(QMainWindow):
    #constructor................................................................
    def __init__(self, ):
        super(Main, self).__init__()
        self.ui = loadUi('mainwindow.ui')
        self.ui.btn_find.clicked.connect(self.btnFileDialog) 
        self.ui.btn_load.clicked.connect(self.btnLoadFile) 
        self.ui.show()    
 
    #button filedialog..........................................................
    def btnFileDialog(self):
        self.file = QtWidgets.QFileDialog.getOpenFileName(self,
                                                         'Open file',
                                                         'e:\\',
                                                         "Video files (*.yml, *.avi)")
        self.ui.edt_file.setText(self.file[0])
    #button loadyml.............................................................
    def btnLoadFile(self):
        file = self.ui.edt_file.toPlainText()
        video = video_sequence_byn(file, 5, 10, 500)
        ret, frame = video.getCurrent()
        while(ret):
            # Capture frame-by-frame
            cv2.imshow('frame',frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            ret, frame = video.getCurrent()

################################################################################
if __name__ == '__main__':
    
    app = QtWidgets.QApplication(sys.argv)
    main = Main()
    sys.exit(app.exec_())

    


##to traduce qt iu to python python -m PyQt5.uic.pyuic visual.ui -o design.py


