import cv2
import numpy
import sys
import glob 
import os

################################################################################
class ShowAnomaly:
    #constructor 
    def __init__(self, folder, fin):
        self.frames = {}
        self.fin = fin
        self.load_bboxes(folder)
        self.GREEN  = (0, 255, 0)
        self.RED    = (0, 0, 255)
    
    #...........................................................................
    #load bounding bbox from file tracklets 
    def load_bboxes(self, folder):
        print('Loading tracklet files:')
        for file in glob.glob(folder + '/*.txt'):
            print(file) 
            
            #looking for the output file
            out_file = file.split('.')[0] + '.out'
            if os.path.isfile(out_file):
              
                fout = open(out_file,'r')
                with open(file) as f: 
                    for line in f: 
                        if len(line) < 1 : continue
                        outl = fout.readline()
                        outs = outl.split(',')
                        data = line.split(',')
                        data[1] = data[1] + outs[1]

                        if int(data[0]) in self.frames:
                            self.frames[int(data[0])].append([int(float(n)) 
                                                     for n in data[1].split()])
                        else:
                            self.frames[int(data[0])] = [[int(float(n)) 
                                                     for n in data[1].split()]]


            else:
                cont = 1
                with open(file) as f: 
                    for line in f: 
                        if len(line) < 1 : continue
                        data = line.split(',')
                        data[1] = data[1] + '0' 
                        if int(data[0]) in self.frames:
                            self.frames[int(data[0])].append([int(float(n)) 
                                                     for n in data[1].split()])
                        else:
                            self.frames[int(data[0])] = [[int(float(n)) 
                                                     for n in data[1].split()]]
                    cont += 1
    #...........................................................................
    #draw bboxes by request
    def draw(self, frame, n_frame):
        if n_frame in self.frames:
            for bbox in self.frames[n_frame]:
                point1 = (bbox[0], bbox[1])
                point2 = (point1[0] + bbox[2],
                          point1[1] + bbox[3])
                if bbox[4] == 0:
                    cv2.rectangle(frame, point1, point2, self.RED, 3)
                else:
                    cv2.rectangle(frame, point1, point2, self.GREEN, 3)
        return frame