import sys
import os
import json
import cv2
import numpy as np
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


ui = uic.loadUiType("VideoShaker.ui")[0]

class MyWindow(QMainWindow, ui):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Video Shaker Tool")
        
        self.dir = None
        self.file_name = None
        self.video_src = None
        
        self.frame_num = []
        self.dx = []
        self.dy = []
      
        self.table.setHorizontalHeaderLabels(["frame","dx","dy"])
        self.pb_delete.setIcon(self.style().standardIcon(QStyle.SP_DialogDiscardButton))
      
        self.pb_import.clicked.connect(self.open)
        self.pb_apply.clicked.connect(self.saveData)
        self.pb_start.clicked.connect(self.moveFrame)
        self.pb_delete.clicked.connect(self.deleteData)
 
        
    def open(self):
        file_name,_ = QFileDialog.getOpenFileName(self,
                            "Open Json File", self.dir,'"json (*.json)')
        if file_name:
            self.lb_import.setText("File : " + str(file_name))
        
        self.file_name = file_name
        if file_name:
            self.parseJson()
        
            
    def parseJson(self):
        
        with open(self.file_name, "r") as file:
            json_data = json.load(file)

        text = json.dumps(json_data, indent=4)
        
        self.json_view.text = QTextBrowser(self.json_view)
        self.json_view.setText(text)       
        self.video_src = json_data['input']
        print(self.video_src)
        
        
    def saveData(self):
        self.frame_num.append(self.le_frame.text())
        self.dx.append(self.le_dx.text())
        self.dy.append(self.le_dy.text())
        row = len(self.dx)-1
        
        frame = QTableWidgetItem(self.le_frame.text())
        dx = QTableWidgetItem(self.le_dx.text())
        dy = QTableWidgetItem(self.le_dy.text())
        self.table.setItem(row,0,frame)
        self.table.setItem(row,1,dx)
        self.table.setItem(row,2,dy)
    

    def moveFrame(self):
        self.lb_start.setText("shaker start ----")
        #start frame
        cap = cv2.VideoCapture(self.video_src)
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        wid = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        hei = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print("fps",fps)
        print("wid",wid)
        print("hei",hei)
        
        # save file name
        dir = os.getcwd()
        base = os.path.basename(self.video_src)
        fname = os.path.splitext(base)[0]
        testPath = dir + "/" + fname + str("_shaked.mp4")
        print(testPath)
        
        out = cv2.VideoWriter(testPath, cv2.VideoWriter_fourcc(*"avc1"), fps, (wid,hei))     
        
        index = 0
        shake_index = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            
            if not ret:
                print('Cannot read video file')
                break
            
            shake_frame = int(self.frame_num[shake_index])
            print("frame index : ", index)
        
            if index == shake_frame:
                print("shake frame index: ", shake_frame)
                shift_x = self.dx[shake_index]
                shift_y = self.dy[shake_index]
                print("dx : ", shift_x)
                print("dy : ", shift_y)
         
                
                M = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
                sftimg = cv2.warpAffine(frame, M, (frame.shape[1], frame.shape[0]))
                out.write(sftimg)    

            
                if shake_index < len(self.frame_num) - 1:
                    print(len(self.frame_num))
                    shake_index += 1
                          
            else:
                out.write(frame)
            
            index += 1
        
        
        out.release()
        
        self.lb_start.setText("shaker Done.")
        
    def deleteData(self):
        delete_row = int(self.table.currentRow())
        print("delete row: ", delete_row)
        self.table.removeRow(delete_row)
        if len(self.frame_num) != 0:
            del self.frame_num[delete_row]
            del self.dx[delete_row]
            del self.dy[delete_row]
            print(self.dx)
        # self.table.takeItem(delete_row,0)
        # self.table.takeItem(delete_row,1)
        # self.table.takeItem(delete_row,2)
        

        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.move(0,0)
    myWindow.show()
    app.exec_()