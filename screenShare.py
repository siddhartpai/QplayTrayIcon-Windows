#!/bin/python
import sys
from PyQt4 import QtGui, Qt, QtCore
from PyQt4.QtGui import QApplication, QCursor, QWidget
import subprocess

croppedOnce=0
class widget(QtGui.QWidget):
	p1x=-1
	p1y=-1
	p2x=-1
	p2y=-1
	t1x=-1
	t2x=-1
	t1y=-1
	t2y=-1
	trayIconObj=None
	def __init__(self):
		super(widget, self).__init__()
		self.initUI()
	def setPoints(self,x1,y1,x2,y2):
		self.p1x=x1
		self.p2x=x2
		self.p1y=y1
		self.p2y=y2
		
	def initUI(self):              
		#self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		self.setWindowOpacity(0.7)
		#self.showMaximized()
		#self.show()
		
	def mousePressEvent(self, QMouseEvent):
		self.p1x=QMouseEvent.pos().x()
		self.p1y=QMouseEvent.pos().y()
		#print "Point 1 x : "+str(self.p1x)+"\nPoint 1 y : "+str(self.p1y)

	def mouseReleaseEvent(self, QMouseEvent):
		self.p2x=QMouseEvent.pos().x()
		self.p2y=QMouseEvent.pos().y()
		self.widgetShow()
		
	def getTrayIcon(self,obj):
		self.trayIconObj=obj
		
	def widgetShow(self,displayWidget=0):
		global croppedOnce
		#Top Left to Bottom Right
		self.t1x=self.p1x
		self.t2x=self.p2x
		self.t1y=self.p1y
		self.t2y=self.p2y
		#Top Right to Bottom Left
		if(self.p1x>self.p2x and self.p1y<self.p2y):
			self.t1x=self.p2x
			self.t1y=self.p1y
			self.t2x=self.p1x
			self.t2y=self.p2y
		#Bottom Right to Top Left
		if(self.p1x>self.p2x and self.p1y>self.p2y):
			self.t1x=self.p2x
			self.t2x=self.p1x
			self.t1y=self.p2y
			self.t2y=self.p1y
		#Bottom Left to Top Right
		if(self.p1x<self.p2x and self.p1y>self.p2y):
			self.t1x=self.p1x
			self.t2x=self.p2x
			self.t1y=self.p2y
			self.t2y=self.p1y
		#print "Point 2 x : "+str(self.p2x)+"\nPoint 2 y : "+str(self.p2y)
		print "Rectangle Co:ord \nleft X:"+str(self.t1x)+"\nleft Y:"+str(self.t2y)
		print "Rectangle width: "+str(self.t2x-self.t1x)
		print "Rectangle height: "+str(self.t2y-self.t1y)
		if(self.t2x-self.t1x!=0 and self.t2y-self.t2x!=0 and croppedOnce==0):
			self.setGeometry(self.t1x,self.t1y,self.t2x-self.t1x,self.t2y-self.t1y)
			if(displayWidget!=1):
				croppedOnce=1
				print "Starting Stream"
				self.trayIconObj.startStream(1)
		if(self.t2x-self.t1x!=0 and self.t2y-self.t2x!=0 and displayWidget==1):
			self.setGeometry(self.t1x,self.t1y,self.t2x-self.t1x,self.t2y-self.t1y)
			self.show()
		#self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		#self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
		#tempW.setWindowFlags(QtCore.Qt.FramelessWindowHint)
	
	


class MouseChange(QWidget):
    
    def __init__(self,parent=None):
	    QWidget.__init__(self,parent)
	    
    def changeCursor(self,parent,cursor):
	    print parent
	    parent.setCursor(QtGui.QCursor(cursor))


class SystemTrayIcon(QtGui.QSystemTrayIcon):

	pid=-1
	parent1=None

	def cropScreen(self):
		global croppedOnce
		croppedOnce=0
		self.parent1.hide()
		self.parent1.setPoints(0,0,1366,768)
		self.parent1.widgetShow(1)
		print self.parent1
		self.changeCursor()
		
	def changeCursor(self):
		changeMouse=MouseChange(self.parent1)
		changeMouse.changeCursor(self.parent1,QtCore.Qt.CrossCursor)
		
	def startStream(self,crop=0):
		if(self.pid!=-1):
			exitAction()
		print "Running ffmpeg"
		if(crop==1):
			width=self.parent1.p2x-self.parent1.p1x
			height=self.parent1.p2y-self.parent1.p2y
			cropPortion=str(width)+':'+str(height)+':'+str(self.parent1.p1x)+':'+str(self.parent1.p1y)
			print cropPortion
			ffmpegCommand='ffmpeg -f dshow  -i video="screen-capture-recorder" -vf crop='+cropPortion+' -r 30 -f rtsp -s 640x480 rtsp://127.0.0.1:7070/live.sdp'
		elif(crop==0):
			ffmpegCommand='ffmpeg -f dshow  -i video="screen-capture-recorder" -r 30 -f rtsp -s 640x480 rtsp://127.0.0.1:7070/live.sdp'
		Process=subprocess.Popen(ffmpegCommand,shell=True)
		self.pid=Process.pid +1
		print self.pid
		print "Successfull"
		
	def secondAction(self):
		self.parent1.hide()
		
	def showWidget(self):
		self.parent1.widgetShow(1)
		
	def killFfmpeg(self):
		subprocess.call("taskkill \PID "+str(self.pid),shell=True)
		
	def exitAction(self):
		print "exit"
		self.killFfmpeg()
		sys.exit()
		
		
	def fourthAction(self):
		print "Fourth"
		
	def thirdAction(self):
		print "Third"
		
	def __init__(self, icon, parent=None):
		print self.parent1
		self.parent1=parent
		print self.parent1
		QtGui.QSystemTrayIcon.__init__(self, icon, parent)
		menu = QtGui.QMenu(parent)
		menu.addAction("Start Streaming",self.startStream)
		menu.addAction("Hide",self.secondAction)
		subMenu=QtGui.QMenu("Third",menu)
		subMenu.addAction("Crop Screen",self.cropScreen)
		subMenu.addAction("Show Cropped Area",self.showWidget)
		menu.addMenu(subMenu)
		menu.addAction("Exit",self.exitAction)
		self.setContextMenu(menu)
        

		
def main():
	print "Hello"
	app = QtGui.QApplication(sys.argv)
	w=widget();
	trayIcon = SystemTrayIcon(QtGui.QIcon("favicon.ico"), w)
	print trayIcon
	w.getTrayIcon(trayIcon)
	trayIcon.show()
	app.exec_()

if __name__ == '__main__':
    main()
