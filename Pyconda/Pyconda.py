import cv2
import numpy
import sys
import yaml
import re
import glob, os

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow
from PyQt5.uic  import loadUi
from video      import video_sequence_by1, video_sequence_byn
from PyQt5.QtGui import QImage, QPixmap
from ShowAnomaly import ShowAnomaly

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


def createDir_by_file(filename):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
################################################################################
################################################################################
#class Main(QMainWindow, Ui_MainWindow):
class Main(QMainWindow):
    #constructor................................................................
    def __init__(self):
        super(Main, self).__init__()

        #loadign previous saved file
        last = open("last","r")
        files = last.readlines()
        if(len(files) < 1 ):
            files = [""]
        last.close()

        #loading qtcreator ui
        self.ui = loadUi('mainwindow.ui')

        #first tab : sequence 
        self.ui.btn_find.clicked.connect(self.btnFileDialog) 
        self.ui.btn_load.clicked.connect(self.btnLoadFile) 
        self.ui.btn_play.clicked.connect(self.btnPlay) 
        self.ui.btn_playstep.clicked.connect(self.btnPlayStep) 

        #second tab : output
        self.ui.btn_find_dir.clicked.connect(self.btnFindDir)  
        self.ui.btn_load_dir.clicked.connect(self.btnLoadDir)  
        self.ui.btn_generate.clicked.connect(self.btnGenerate)  
        self.ui.btn_record.clicked.connect(self.btnRecord)  
        
        #edit loading yml file
        self.ui.edt_file.setText(files[0]) 
        
        self.ui.show()    

    ############################################################################
    ############################################################################
    ###Tab1-sequence 
    #button filedialog..........................................................
    def btnFileDialog(self):
        file = QtWidgets.QFileDialog.getOpenFileName(self,
                                                     'Open file',
                                                     'Z:\\tmp\\Anomalies\\Videos\\Bank',
                                                     "Yml files (*.yml; *.avi)")
        self.ui.edt_file.setText(file[0])
    #button loadyml............................................................. 
    def btnLoadFile(self):
        self.file = self.ui.edt_file.toPlainText()

        if os.path.isfile(self.file) == False:
            print("File does not exits!")
            return
        
        prop    = readYAMLFile(self.file)
        
        self.video_file = prop['video_file'] 
        self.video      = video_sequence_byn(prop['video_file'], 
                                            prop['video_step'], 
                                            prop['video_ini'], 
                                            prop['video_fin'] )

        self.out_path =  prop['video_out_path']
        
        self.ui.edt_ini.setText( str(self.video.pos_ini) )
        self.ui.edt_fin.setText( str(self.video.pos_fin) )
        self.ui.edt_row.setText( str(self.video.width) )
        self.ui.edt_col.setText( str(self.video.height) )
        self.ui.edt_frame.setText(str(self.video.current))

        ret, frame = self.video.getCurrent()
        he, wi, ch = frame.shape
        pix = mat2Qpix(frame)
        
        #showing the video window
        self.seq = loadUi('window.ui')
        self.seq.lbl_image.setPixmap(pix)
        self.seq.lbl_image.setGeometry(QtCore.QRect(0, 0, wi, he))
        self.seq.resize(wi+5, he + 35)
        self.seq.show()

        #loading anomalies bounding boxes and anomalies
        self.show_anomaly = ShowAnomaly(self.out_path, self.video.pos_fin)

        #saving current file
        last = open("last","w")
        last.write(self.file)
        last.close()
    
        return

    #button play................................................................
    def btnPlay(self):
        frms = int(self.ui.edt_frame.text())
        self.video.setCurrent(frms)
        ret, frame = self.video.getCurrent()
        while(ret):
            frame = self.show_anomaly.draw(frame, self.video.current)
            pix = mat2Qpix(frame)
            self.seq.lbl_image.setPixmap(pix)
            self.seq.lbl_image.repaint()
            
            self.ui.edt_frame.setText(str(self.video.current))
            self.ui.repaint()

            ret, frame = self.video.getCurrent()
    
    #...............................................................................
    #record video...................................................................
    def saveVideo2File(self, dir_name, file_name, ini, fin, video, fps):

        tok = '_' + str(ini) + '_' + str(fin) 
        file = dir_name + "/" + file_name + tok + ".avi"
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(  file, fourcc, fps, 
                                (int(video.width), int(video.height)))
                                
        self.video.setCurrent(ini)
        ret, frame = self.video.getCurrent()

        self.ui.lbl_record.setText('Recording') 
        while(ret and self.video.current <= fin):
            frame = self.show_anomaly.draw(frame, self.video.current)
            pix = mat2Qpix(frame)
            out.write(frame)

            self.seq.lbl_image.setPixmap(pix)
            self.seq.lbl_image.repaint()
            
            self.ui.edt_frame.setText(str(self.video.current))
            self.ui.repaint()

            #so momentaneo
            #fileid = dir_name + "/" + file_name + tok + '_'+ str(self.video.current) + '.jpg'
            
            #cv2.imwrite( fileid, frame)

            ret, frame = self.video.getCurrent()
        out.release()
        self.ui.lbl_record.setText('') 
        print ('Writting in: ' + file)
        return file_name

    #button playstep............................................................
    def btnPlayStep(self):
        frms = int(self.ui.edt_frame.text())
        self.video.setCurrent(frms)
        ret, frame = self.video.getCurrent()
        if(ret):
            frame = self.show_anomaly.draw(frame, self.video.current)
            pix = mat2Qpix(frame)
            self.seq.lbl_image.setPixmap(pix)
            self.seq.lbl_image.repaint()
            
            self.ui.edt_frame.setText(str(self.video.current))
            self.ui.repaint()

    #button playstep............................................................
    def btnRecord(self):
        if(not self.video.cap.isOpened()):
            return

        fps = int(self.video.cap.get(cv2.CAP_PROP_FPS))
        dir_name = os.path.dirname( self.video_file )
        file_name = os.path.basename( self.video_file ).split('.')[0]

        ini = int(self.ui.edt_frame.text())
        fin = self.video.pos_fin

        self.saveVideo2File(dir_name, file_name, ini, fin, self.video, fps)        
        
    ############################################################################
    ############################################################################
    def btnFindDir(self):
        dir = QtWidgets.QFileDialog.getExistingDirectory(self, 
                                    'Select a folder:', 
                                    'z:\\tmp\\anomalies\\',
                                    QtWidgets.QFileDialog.DontResolveSymlinks)
        self.ui.edt_dir.setText(dir)
    
    #button load_dir............................................................
    def btnLoadDir(self):
        self.dir = self.ui.edt_dir.toPlainText().replace('\\','/')
        token    = self.ui.edt_token.text()
        
        self.file_list = ''
        os.chdir(self.dir)
        for file in glob.glob(token):
            self.file_list = self.file_list + file +  '\n'
        self.ui.edt_list_file.setText(self.file_list)
        

    #button generate............................................................
    def btnGenerate(self):
        
        list = self.file_list.split('\n')
        del list[-1]

        if len(list):
            header = "%YAML:1.0"
            dir    = self.dir + "/"
            dirscripts = dir + 'scripts/'
            print('Generating ...')
            for fl in list:
                name =  fl.split('.')[0]
                file_name = dirscripts + name + '/' + name + '_conf.yml'

                createDir_by_file ( file_name ) 
                tmp = open( file_name, "w")
                tmp.write( header )
                tmp.write( "\nvideo_file: \""   + dir + fl + "\"")
                tmp.write( "\nvideo_seq: \""    + dir + name + '.txt' + "\"")
                tmp.write( "\nstep: "           + self.ui.edt_step.text() )
                tmp.write( "\nresize: "         + self.ui.edt_rze.text() )
                tmp.close()

                print(file_name)

  ################################################################################

if __name__ == '__main__':
    
    app = QtWidgets.QApplication(sys.argv)
    main = Main()
    sys.exit(app.exec_())
             
   
    
##to traduce qt iu to python python -m PyQt5.uic.pyuic visual.ui -o design.py
