import sys

sys.path.append('/usr/lib/pymodules/python2.7/')
sys.path.append('/usr/lib/python2.7/dist-packages')
sys.path.append('/usr/lib/pyshared/python2.7/')
sys.path.append('/usr/local/lib/python2.7/site-packages/')

from PyQt4.QtCore import QUrl
from PyQt4 import QtWebKit
from PyQt4 import QtCore
from PyQt4.QtGui import *
from PyQt4 import QtGui
import cv2
import ColorConverter


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

    def set_hover(self, hoverStyle):
        self.hoverStyle = hoverStyle
        self.fhs = open(self.hoverStyle)
        self.setStyleSheet(self.fhs.read())

    def set_style(self, style):
        self.style = style
        self.fs = open(self.style)
        self.setStyleSheet(self.fs.read())


class VideoWidget(QWidget):
    """ A class for rendering video coming from OpenCV """

    def __init__(self, color_deficit, parent=None):

        QWidget.__init__(self)
        self.imageCount = 1
        self.recCount = 1
        self.toRecord = False
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
        self._timer.start(50)

    def design(self):

        self.hoverStyle = "newvideoHoverStyle.stylesheet"
        self.sshFile = "newstyle.stylesheet"

        with open(self.sshFile, "r") as fh:
            self.setStyleSheet(fh.read())


        image = QtGui.QLabel(self)
        pixmap = QPixmap("label.png")
        image.setAccessibleName("Label")
        image.setPixmap(pixmap)
        image.move(self.width * 0.2, self.height * 0.85)
        image.show()

        self.zoom = HoverEvent(self.sshFile, self.hoverStyle, "Zoom", self)
        self.zoom.move(self.width * 0.2 + 513, self.height * 0.85 + 4)
        self.zoom.clicked.connect(self.open_zoom)

        self.adjust = HoverEvent(self.sshFile, self.hoverStyle, "Adj", self)
        self.adjust.move(self.width * 0.2 + 20, self.height * 0.85 + 4)
        self.adjust.clicked.connect(self.open_adj)

        self.deficiency = HoverEvent(self.sshFile, self.hoverStyle, "Def", self)
        self.deficiency.move(self.width * 0.2 + 283, self.height * 0.85 + 4)
        self.deficiency.clicked.connect(self.open_def)

        fullScreen = HoverEvent(self.sshFile, self.hoverStyle, "FullScreen", self)
        fullScreen.move(self.width * 0.2 + 373, self.height * 0.85 + 4)

        capture = HoverEvent(self.sshFile, self.hoverStyle, "Capture", self)
        capture.move(self.width * 0.2 + 143, self.height * 0.85 + 4)
        capture.clicked.connect(self.capture_image)

        self.rec = HoverEvent(self.sshFile, self.hoverStyle, "Rec", self)
        self.rec.move(self.width * 0.2 + 213, self.height * 0.85 + 4)
        self.rec.clicked.connect(self.record)

        self.zoomScroll = QtGui.QScrollBar(self)
        self.zoomScroll.setMaximum(-1)
        self.zoomScroll.setMinimum(-100)
        self.zoomScroll.move(self.width * 0.2 + 594, self.height * 0.85 - 218)
        self.zoomScroll.valueChanged.connect(self.set_key)
        self.zoomScroll.hide()

        self.scale = QtGui.QScrollBar(self)
        self.scale.setMaximum(0)
        self.scale.setMinimum(-100)
        self.scale.setValue(-100)
        self.scale.move(self.width * 0.2 - 22, self.height * 0.85 - 218)
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

        if self.toRecord:
            self.out.write(image)

        self.update()

    def capture_image(self):
        cv2.imwrite("/Users/orbarda/Desktop/BinocolorsImage" + str(self.imageCount) + ".jpg", self._frame)
        self.imageCount += 1
        # img = numpy.zeros([self.width, self.height, 3], dtype=numpy.uint8)
        # img.fill(255)
        # self._image = self._build_image(img)
        self.update()
        cv2.waitKey(500)

    def record(self):

        if not self.toRecord:
            self.rec.setAccessibleName("RecRed")
            self.rec.set_style(self.sshFile)
            self.rec.set_hover(self.hoverStyle)
            self.out = cv2.VideoWriter("BinocolorsVideo" + str(self.recCount) + ".avi", -1, 20.0, (1024, 768))
            self.toRecord = True
            self.recCount += 1
        else:
            self.rec.setAccessibleName("Rec")
            self.rec.set_style(self.sshFile)
            self.rec.set_hover(self.hoverStyle)
            self.toRecord = False

    def open_def(self):

        if not self.isOnDef:

            self.deficiency.set_style(self.hoverStyle)

            self.protan = HoverEvent(self.sshFile, self.hoverStyle, "Protan", self)
            self.protan.move(self.width * 0.2 + 284, self.height * 0.85 - 101)
            self.protan.clicked.connect(self.set_to_p)

            self.deutan = HoverEvent(self.sshFile, self.hoverStyle, "Deutan", self)
            self.deutan.move(self.width * 0.2 + 284, self.height * 0.85 - 52)
            self.deutan.clicked.connect(self.set_to_d)

            self.tritan = HoverEvent(self.sshFile, self.hoverStyle, "Tritan", self)
            self.tritan.move(self.width * 0.2 + 284, self.height * 0.85 - 26)
            self.tritan.clicked.connect(self.set_to_t)

            self.isOnDef = True
        else:
            self.deficiency.set_style(self.sshFile)

            self.protan.hide()
            self.deutan.hide()
            self.tritan.hide()

            self.isOnDef = False

    def open_zoom(self):

        if not self.isOnZoom:
            self.zoom.set_style(self.hoverStyle)
            self.zoomScroll.show()
            self.isOnZoom = True

        else:
            self.zoom.set_style(self.sshFile)
            self.zoomScroll.hide()
            self.isOnZoom = False

    def open_adj(self):

        if not self.isOnAdj:
            self.adjust.set_style(self.hoverStyle)
            self.scale.show()
            self.isOnAdj = True

        else:
            self.adjust.set_style(self.sshFile)
            self.scale.hide()
            self.isOnAdj = False

    def set_to_d(self):
        self.color_converter.set_deficit('d')

    def set_to_p(self):
        self.color_converter.set_deficit('p')

    def set_to_t(self):
        self.color_converter.set_deficit('t')

    def set_key(self):
        self.color_converter.set_key(-1.0 * self.scale.value(), -1.0 * self.zoomScroll.value())


class DeficiencyWindow(QWidget):

    def __init__(self):
        QWidget.__init__(self)

        self.width = 800
        self.height = 600

        self.sshFile="newstyle2.stylesheet"
        self.hoverStyle = "newhoverstyle.stylesheet"

        with open(self.sshFile, "r") as fh:

            self.setStyleSheet(fh.read())

        self.setGeometry(300, 50, self.width, self.height)

        image = QtGui.QLabel(self)
        pixmap = QPixmap("Secondwindow/newBinocolors1.png")
        image.setPixmap(pixmap)
        image.move(self.width * 0.2, self.height * 0.1)
        image.show()

        red = HoverEvent(self.sshFile, self.hoverStyle, "Red", self)
        red.move(260, 300)
        red.clicked.connect(self.launch_clickedP)

        green = HoverEvent(self.sshFile, self.hoverStyle, "Green", self)
        green.move(260, 370)
        green.clicked.connect(self.launch_clickedD)

        blue = HoverEvent(self.sshFile, self.hoverStyle, "Blue", self)
        blue.move(260, 440)
        blue.clicked.connect(self.launch_clickedT)

        p = self.palette()
        p.setBrush(QPalette.Background, QBrush(QPixmap("Secondwindow/background.jpg")))
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

    def __init__(self):
        QWidget.__init__(self)

        self.width = 800
        self.height = 600

        self.sshFile="newstyle1.stylesheet"
        self.hoverStyle = "newhoverstyle.stylesheet"

        fh = open(self.sshFile, "r")
        self.setStyleSheet(fh.read())

        self.setGeometry(300, 50, self.width, self.height)

        image = QtGui.QLabel(self)
        pixmap = QPixmap("Firstwindow/newBinocolors1.png")
        image.setAccessibleName("logo")
        image.setPixmap(pixmap)
        image.move(self.width * 0.2, self.height * 0.1)
        image.show()

        label = QtGui.QLabel(self)
        pixmap = QPixmap("Firstwindow/question.png")
        label.setAccessibleName("question")
        label.setPixmap(pixmap)
        label.move(self.width * 0.19, self.height * 0.44)
        label.show()

        # label = QtGui.QLabel(self)
        # label.setAccessibleName("question")
        # label.setText("<font size= '6' color='black'> Do you know what type of color blindness you have? </font>")
        # label.move(self.width * 0.12, self.height * 0.45)
        # label.show()

        p = self.palette()
        p.setBrush(QPalette.Background, QBrush(QPixmap("Firstwindow/background.jpg")))
        self.setPalette(p)

        # p = self.palette()
        # p.setColor(self.backgroundRole(), QtCore.Qt.white)
        # self.setPalette(p)

        yes = HoverEvent(self.sshFile, self.hoverStyle, "Yes", self)
        yes.move(300, 400)
        yes.clicked.connect(self.launch_if_yes)

        no = HoverEvent(self.sshFile, self.hoverStyle, "No", self)
        no.move(400, 400)
        no.clicked.connect(self.open_test)

    def launch_if_yes(self):

        self.nextWindow = DeficiencyWindow()
        self.nextWindow.show()
        self.hide()

    def open_test(self):

        self.test = WebTest()
        self.test.show()
        self.hide()
        # webbrowser.open('http://www.color-blindness.com/fm100hue/FM100Hue.swf?width=980&height=500')


class WebTest(QWidget):

    def __init__(self):
        QWidget.__init__(self)

        self.sshFile = "newstyle1.stylesheet"
        self.hoverStyle = "newhoverstyle.stylesheet"

        fh = open(self.sshFile, "r")
        self.setStyleSheet(fh.read())

        self.setGeometry(300, 0, 800, 600)

        view = QtWebKit.QWebView(self)
        view.setGeometry(-20, 0, 850, 600)

        url = "index.html#"
        view.setWindowTitle(url)
        view.load(QUrl(url))
        view.show()

        button = HoverEvent(self.sshFile, self.hoverStyle, "Html", self)
        button.setText("I'm done")
        button.move(610, 220)
        button.clicked.connect(self.open_next_window)

    def open_next_window(self):
        self.testResult = TestResult()
        self.testResult.show()
        self.hide()



class TestResult(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.sshFile = "newstyle1.stylesheet"
        self.hoverStyle = "newhoverstyle.stylesheet"

        fh = open(self.sshFile, "r")
        self.setStyleSheet(fh.read())

        self.setGeometry(300, 0, 800, 600)

        view = QtWebKit.QWebView(self)
        view.setGeometry(-20, 0, 850, 600)

        url = "index2.html#"
        view.setWindowTitle(url)
        view.load(QUrl(url))
        view.show()

        button = HoverEvent(self.sshFile, self.hoverStyle, "Finish", self)
        button.setText("Finish")
        button.move(610, 210)
        button.clicked.connect(self.open_next_window)

    def open_next_window(self):

        self.nextWindow = DeficiencyWindow()
        self.nextWindow.show()
        self.hide()


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    while True:

        welcomeWindow = WelcomeWindow()

        welcomeWindow.show()

        app.exec_()

