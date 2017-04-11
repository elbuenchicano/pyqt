import cv2
import numpy
import sys
import yaml
import re

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow
from PyQt5.uic  import loadUi
from video      import video_sequence_by1, video_sequence_byn
from PyQt5.QtGui import QImage, QPixmap


def mat2Qpix(frame):
    he, wi, ch = frame.shape
    bytes   = 3 * wi
    qImg    = QImage(frame.data, wi, he, bytes, QImage.Format_RGB888)
    pix     = QPixmap(qImg)
    return pix


def readYAMLFile(fileName):
    ret = {}
    skip_lines=1    # Skip the first line which says "%YAML:1.0". Or replace it with "%YAML 1.0"
    with open(fileName) as fin:
        for i in range(skip_lines):
            fin.readline()
        yamlFileOut = fin.read()
        #myRe = re.compile(r":([^ ])")   # Add space after ":", if it doesn't exist. Python yaml requirement
        #yamlFileOut = myRe.sub(r': \1', yamlFileOut)
        ret = yaml.load(yamlFileOut)
    return ret


################################################################################
#class Main(QMainWindow, Ui_MainWindow):
class Main(QMainWindow):
    #constructor................................................................
    def __init__(self, ):
        super(Main, self).__init__()

        last = open("last","r")
        files = last.readlines()
        if(len(files) < 1 ):
            files = [""]
        last.close()

        self.ui = loadUi('mainwindow.ui')
        self.ui.btn_find.clicked.connect(self.btnFileDialog) 
        self.ui.btn_load.clicked.connect(self.btnLoadFile) 
        self.ui.edt_file.setText(files[0]) 
        self.ui.show()    
 
    #button filedialog..........................................................
    def btnFileDialog(self):
        file = QtWidgets.QFileDialog.getOpenFileName(self,
                                                     'Open file',
                                                     'e:\\',
                                                     "Yml files (*.yml; *.avi)")
        self.ui.edt_file.setText(file[0])
    #button loadyml............................................................. 
    def btnLoadFile(self):
        self.file = self.ui.edt_file.toPlainText()
        
        prop    = readYAMLFile(self.file)
        
        video   = video_sequence_byn(prop['seq_file'], 
                                     prop['seq_step'], 
                                     prop['seq_ini'], 
                                     prop['seq_fin'] )
        
        ret, frame = video.getCurrent()
        he, wi, ch = frame.shape
        pix = mat2Qpix(frame)
        
        #showing the video window
        self.seq = loadUi('window.ui')
        self.seq.lbl_image.setPixmap(pix)
        self.seq.lbl_image.setGeometry(QtCore.QRect(0, 0, wi, he))
        self.seq.resize(wi+5, he + 35)
        self.seq.show()

        last = open("last","w")
        last.write(self.file)
        last.close()

        

################################################################################

if __name__ == '__main__':
    
    app = QtWidgets.QApplication(sys.argv)
    main = Main()
    sys.exit(app.exec_())
             
    
    


##to traduce qt iu to python python -m PyQt5.uic.pyuic visual.ui -o design.py
#while(ret):
            #    # Capture frame-by-frame
            #    cv2.imshow('frame',frame)
            #    if cv2.waitKey(1) & 0xFF == ord('q'):
            #        break
            #    ret, frame = video.getCurrent()

