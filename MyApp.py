import sys

sys.path.append('/usr/lib/pymodules/python2.7/')
sys.path.append('/usr/lib/python2.7/dist-packages')
sys.path.append('/usr/lib/pyshared/python2.7/')
sys.path.append('/usr/local/lib/python2.7/site-packages/')

from PyQt4 import QtCore

from PyQt4.QtGui import *

from PyQt4 import QtGui

import numpy

import cv2

import ColorConverter

import webbrowser

class IplQImage(QImage):
    def __init__(self, frame):
        iplimage = cv2.cv.CreateImageHeader((frame.shape[1], frame.shape[0]), cv2.cv.IPL_DEPTH_8U, 3)
        cv2.cv.SetData(iplimage, frame.tostring(), frame.dtype.itemsize * 3 * frame.shape[1])

        alpha = cv2.cv.CreateMat(iplimage.height, iplimage.width, cv2.cv.CV_8UC1)
        cv2.cv.Rectangle(alpha, (0, 0), (iplimage.width, iplimage.height), cv2.cv.ScalarAll(255), -1)
        rgba = cv2.cv.CreateMat(iplimage.height, iplimage.width, cv2.cv.CV_8UC4)
        cv2.cv.Set(rgba, (1, 2, 3, 4))
        cv2.cv.MixChannels([iplimage, alpha],[rgba], [(0, 0),(1, 1),(2, 2),(3, 3)])

        self.__imagedata = rgba.tostring()
        super(IplQImage, self).__init__(self.__imagedata, iplimage.width, iplimage.height, QImage.Format_RGB32)


class VideoWidget(QWidget):
    """ A class for rendering video coming from OpenCV """

    def __init__(self, color_deficit, parent=None):
        QWidget.__init__(self)
        self.width = 1024
        self.height = 768
        self.capture = cv2.VideoCapture(0)
        # Take one frame to query height
        ret, frame = self.capture.read()
        self.color_converter = ColorConverter.ColorConverter(color_deficit)
        image = self.color_converter.convert(frame)
        self.setMinimumSize(self.width, self.height)
        self.setMaximumSize(self.minimumSize())
        self.design()
        self._frame = None
        self._image = self._build_image(image)
        # Paint every 50 ms
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.queryFrame)
        self._timer.start(50)

    # def enterEvent(self, event):
    #     self.mouseover.show()
    #
    # def leaveEvent(self, event):
    #     self.mouseover.hide()

    def design(self):

        sshFile = "style.stylesheet"
        with open(sshFile, "r") as fh:
            self.setStyleSheet(fh.read())

        self.setWindowTitle('PyQt - OpenCV Test')

        # self.mouseover = QtGui.QPushButton(self)
        # self.mouseover.setAccessibleName("Red")
        # self.mouseover.move(100, 100)
        # self.mouseover.setMouseTracking(True)

        red = QtGui.QPushButton(self)
        red.setAccessibleName("Red")
        red.move(self.width * 0.13, self.height * 0.85)
        red.clicked.connect(self.set_to_d)
        red.show()

        green = QtGui.QPushButton(self)
        green.setAccessibleName("Green")
        green.move(self.width * 0.13 + 270, self.height * 0.85)
        green.clicked.connect(self.set_to_p)
        green.show()

        blue = QtGui.QPushButton(self)
        blue.setAccessibleName("Blue")
        blue.move(self.width * 0.13 + 540, self.height * 0.85)
        blue.clicked.connect(self.set_to_t)
        blue.show()

        self.scale = QtGui.QScrollBar(self)
        self.scale.setMaximum(0)
        self.scale.setMinimum(-100)
        self.scale.setValue(-100)
        self.scale.move(self.width * 0.93, self.height * 0.125)
        self.scale.valueChanged.connect(self.set_key)
        self.scale.show()

        self.zoom = QtGui.QScrollBar(self)
        self.zoom.setMaximum(0)
        self.zoom.setMinimum(-100)
        self.zoom.move(self.width * 0.93, self.height * 0.125 + 300)
        self.zoom.valueChanged.connect(self.set_key)
        self.zoom.setWindowTitle("zoom")
        self.zoom.show()

    # def set_key(self):
    #     self.widget.set_key(-1 * self.scale.value(), -1 * self.zoom.value())

    def _build_image(self, frame):
        self._frame = frame
        # if frame.origin == cv.IPL_ORIGIN_TL:
        #     cv.Copy(frame, self._frame)
        # else:
        #     cv.Flip(frame, self._frame, 0)
        return IplQImage(numpy.fliplr(self._frame))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(QtCore.QPoint(0, 0), self._image)

    def queryFrame(self):
        ret, frame = self.capture.read()
        image = self.color_converter.convert(frame)
        self._image = self._build_image(image)
        self.update()

    def set_to_d(self):
        self.color_converter.set_deficit('d')

    def set_to_p(self):
        self.color_converter.set_deficit('p')

    def set_to_t(self):
        self.color_converter.set_deficit('t')

    def set_key(self):
        self.color_converter.set_key(-1 * self.scale.value(), -1 * self.zoom.value())


class DeficiencyWindow(QWidget):

    def __init__(self, parent = None):
        QWidget.__init__(self)

        sshFile="style1.stylesheet"

        with open(sshFile, "r") as fh:

            self.setStyleSheet(fh.read())


        self.setGeometry(300,50,600,400)


        image = QtGui.QLabel(self)

        pixmap = QPixmap("Binocolors.png")

        image.setPixmap(pixmap)

        image.move(150,0)

        image.show()



        label = QtGui.QLabel(self)

        label.setText("What type of colorblind are you?")

        label.move(180, 130)



        button = QPushButton(self)

        button.setText("Deuteranope deficiency")

        button.move(120, 180)

        button.clicked.connect(self.launch_clickedD)

        button.show()



        button = QPushButton(self)

        button.setText("Protanope deficiency")

        button.move(120, 250)

        button.clicked.connect(self.launch_clickedP)

        button.show()



        button = QPushButton(self)

        button.setText("Tritanope deficiency")

        button.move(120, 320)

        button.clicked.connect(self.launch_clickedT)

        button.show()



        p = self.palette()

        p.setColor(self.backgroundRole(), QtCore.Qt.white)

        self.setPalette(p)

    #def open_test():

    #    webbrowser.open('http://www.color-blindness.com/fm100hue/FM100Hue.swf?width=980&height=500')

    def launch_clickedD(self):

        self.videoWindow = VideoWidget('d')
        self.videoWindow.show()
        self.hide()

    def launch_clickedP(self):

        self.videoWindow = VideoWidget('p')
        self.videoWindow.show()
        self.hide()


    def launch_clickedT(self):

        self.videoWindow = VideoWidget('t')
        self.videoWindow.show()
        self.hide()

class WelcomeWindow(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self)

        sshFile="style1.stylesheet"
        with open(sshFile, "r") as fh:
            self.setStyleSheet(fh.read())

        self.setGeometry(300, 50, 600, 400)

        image = QtGui.QLabel(self)
        pixmap = QPixmap("Binocolors.png")
        image.setPixmap(pixmap)
        image.move(150, 0)
        image.show()

        label = QtGui.QLabel(self)
        label.setText("Do you know what type of colorblind are you?")
        label.move(145, 150)

        p = self.palette()
        p.setColor(self.backgroundRole(), QtCore.Qt.white)
        self.setPalette(p)

        button = QPushButton(self)
        button.setText("Yes!")
        button.move(120, 220)
        button.clicked.connect(self.launch_if_yes)
        button.show()

        button = QPushButton(self)
        button.setText("No, Lets Find Out!")
        button.move(120, 300)
        button.clicked.connect(self.open_test)
        button.show()

    def launch_if_yes(self):

        self.nextWindow = DeficiencyWindow()
        self.nextWindow.show()
        self.hide()

    def open_test(self):

        webbrowser.open('http://www.color-blindness.com/fm100hue/FM100Hue.swf?width=980&height=500')



if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    welcomeWindow = WelcomeWindow()

    welcomeWindow.show()

    app.exec_()
