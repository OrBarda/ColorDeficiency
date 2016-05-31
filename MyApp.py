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
        cv2.cv.MixChannels([iplimage, alpha], [rgba], [(0, 0), (1, 1), (2, 2), (3, 3)])

        self.__imagedata = rgba.tostring()
        super(IplQImage, self).__init__(self.__imagedata, iplimage.width, iplimage.height, QImage.Format_RGB32)


class HoverEvent(QPushButton):

    def __init__(self, style, hoverStyle, name, parent):

        self.name = name
        self.hoverStyle = hoverStyle
        self.style = style

        QPushButton.__init__(self, parent)

        self.fhs = open(self.hoverStyle)
        self.fs = open(self.style)

        self.setStyleSheet(self.fs.read())

        self.setAccessibleName(self.name)
        self.setMouseTracking(True)
        self.show()

    def enterEvent(self, event):

        self.fhs.seek(0)
        self.setStyleSheet(self.fhs.read())

    def leaveEvent(self, event):

        self.fs.seek(0)
        self.setStyleSheet(self.fs.read())


class VideoWidget(QWidget):
    """ A class for rendering video coming from OpenCV """

    def __init__(self, color_deficit, parent=None):

        QWidget.__init__(self)
        self.imageCount = 1
        self.isOnZoom = False
        self.isOnAdj = False
        self.isOnDef = False
        self.width = 1024
        self.height = 768

        self.setMinimumSize(self.width, self.height)
        self.setMaximumSize(self.minimumSize())
        self.design()

        self.capture = cv2.VideoCapture(0)
        # Take one frame to query height
        ret, frame = self.capture.read()
        self.color_converter = ColorConverter.ColorConverter(color_deficit)
        image = self.color_converter.convert(frame)
        self._image = self._build_image(image)
        # Paint every 50 ms
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.queryFrame)
        self._timer.start(10)

    def design(self):

        self.toolbarStyle = "toolbarStyle.stylesheet"
        self.hoverStyle = "videoHoverStyle.stylesheet"
        self.sshFile = "style.stylesheet"

        with open(self.sshFile, "r") as fh:
            self.setStyleSheet(fh.read())

        zoom = HoverEvent(self.sshFile, self.hoverStyle, "Zoom", self)
        zoom.move(self.width * 0.13 + 590, self.height * 0.883)
        zoom.clicked.connect(self.open_zoom)

        adjust = HoverEvent(self.sshFile, self.hoverStyle, "Adj", self)
        adjust.move(self.width * 0.13 + 506, self.height * 0.883)
        adjust.clicked.connect(self.open_adj)

        deficiency = HoverEvent(self.sshFile, self.hoverStyle, "Def", self)
        deficiency.move(self.width * 0.13 + 404, self.height * 0.883)
        deficiency.clicked.connect(self.open_def)

        fullScreen = HoverEvent(self.sshFile, self.hoverStyle, "FullScreen", self)
        fullScreen.move(self.width * 0.13 + 320, self.height * 0.883)
        fullScreen.clicked.connect(self.set_to_t)

        capture = HoverEvent(self.sshFile, self.hoverStyle, "Capture", self)
        capture.move(self.width * 0.13 + 236, self.height * 0.883)
        capture.clicked.connect(self.capture_image)

        rec = HoverEvent(self.sshFile, self.hoverStyle, "Rec", self)
        rec.move(self.width * 0.13 + 117, self.height * 0.883)
        rec.clicked.connect(self.set_to_t)

        self.zoom = QtGui.QScrollBar(self)
        self.zoom.setMaximum(0)
        self.zoom.setMinimum(-100)
        self.zoom.move(self.width * 0.13 + 590, self.height * 0.883 - 277)
        self.zoom.valueChanged.connect(self.set_key)
        self.zoom.hide()

        self.scale = QtGui.QScrollBar(self)
        self.scale.setMaximum(0)
        self.scale.setMinimum(-100)
        self.scale.setValue(-100)
        self.scale.move(self.width * 0.13 + 506, self.height * 0.883 - 277)
        self.scale.valueChanged.connect(self.set_key)
        self.scale.hide()

    def _build_image(self, frame):
        self._frame = frame
        # if frame.origin == cv.IPL_ORIGIN_TL:
        #     cv.Copy(frame, self._frame)
        # else:
        #     cv.Flip(frame, self._frame, 0)
        # return IplQImage(numpy.fliplr(self._frame))
        return IplQImage(self._frame)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(QtCore.QPoint(0, 0), self._image)

    def queryFrame(self):
        ret, frame = self.capture.read()
        image = self.color_converter.convert(frame)
        self._image = self._build_image(image)
        self.update()

    def capture_image(self):
        cv2.imwrite("/Users/orbarda/Desktop/BinocolorsImage" + str(self.imageCount) + ".jpg", self._frame)
        self.imageCount += 1
        # img = numpy.zeros([self.width, self.height, 3], dtype=numpy.uint8)
        # img.fill(255)
        # self._image = self._build_image(img)
        self.update()
        cv2.waitKey(500)


    def open_def(self):

        if(self.isOnDef == False):

            self.protan = HoverEvent(self.sshFile, self.hoverStyle, "Protan", self)
            self.protan.move(self.width * 0.13 + 406, self.height * 0.89 - 116)
            self.protan.clicked.connect(self.set_to_p)

            self.deutan = HoverEvent(self.sshFile, self.hoverStyle, "Deutan", self)
            self.deutan.move(self.width * 0.13 + 406, self.height * 0.89 - 75)
            self.deutan.clicked.connect(self.set_to_d)

            self.tritan = HoverEvent(self.sshFile, self.hoverStyle, "Tritan", self)
            self.tritan.move(self.width * 0.13 + 406, self.height * 0.89 - 34)
            self.tritan.clicked.connect(self.set_to_t)

            self.isOnDef = True
        else:
            self.protan.hide()
            self.deutan.hide()
            self.tritan.hide()

            self.isOnDef = False

    def open_zoom(self):

        if(self.isOnZoom == False):

            self.zoom.show()
            self.isOnZoom = True

        else:
            self.zoom.hide()
            self.isOnZoom = False

    def open_adj(self):

        if(self.isOnAdj == False):

            self.scale.show()
            self.isOnAdj = True

        else:
            self.scale.hide()
            self.isOnAdj = False

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

        self.sshFile="style2.stylesheet"
        self.hoverStyle = "hoverstyle.stylesheet"

        with open(self.sshFile, "r") as fh:

            self.setStyleSheet(fh.read())

        self.setGeometry(300,50,600,400)

        image = QtGui.QLabel(self)
        pixmap = QPixmap("Binocolors.png")
        image.setPixmap(pixmap)
        image.move(150,0)
        image.show()

        # label = QtGui.QLabel(self)
        # label.setText("What type of colorblind are you?")
        # label.move(180, 130)

        red = HoverEvent(self.sshFile, self.hoverStyle, "Red", self)
        red.move(130, 150)
        red.clicked.connect(self.launch_clickedP)

        green = HoverEvent(self.sshFile, self.hoverStyle, "Green", self)
        green.move(130, 230)
        green.clicked.connect(self.launch_clickedD)

        blue = HoverEvent(self.sshFile, self.hoverStyle, "Blue", self)
        blue.move(130, 310)
        blue.clicked.connect(self.launch_clickedT)

        p = self.palette()
        p.setColor(self.backgroundRole(), QtCore.Qt.white)
        self.setPalette(p)

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

        self.sshFile="style1.stylesheet"
        self.hoverStyle = "hoverstyle.stylesheet"

        fh = open(self.sshFile, "r")
        self.setStyleSheet(fh.read())

        self.setGeometry(300, 50, 600, 400)

        image = QtGui.QLabel(self)
        pixmap = QPixmap("Binocolors.png")
        image.setAccessibleName("logo")
        image.setPixmap(pixmap)
        image.move(150, 0)
        image.show()

        label = QtGui.QLabel(self)
        pixmap = QPixmap("question1.png")
        label.setAccessibleName("question")
        label.setPixmap(pixmap)
        label.move(100, 130)
        label.show()

        # p = self.palette()
        # p.setBrush(QPalette.Background, QBrush(QPixmap("images")))
        # self.setPalette(p)

        p = self.palette()
        p.setColor(self.backgroundRole(), QtCore.Qt.white)
        self.setPalette(p)

        yes = HoverEvent(self.sshFile, self.hoverStyle, "Yes", self)
        yes.move(120, 200)
        yes.clicked.connect(self.launch_if_yes)

        no = HoverEvent(self.sshFile, self.hoverStyle, "No", self)
        no.move(120, 290)
        no.clicked.connect(self.open_test)

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
