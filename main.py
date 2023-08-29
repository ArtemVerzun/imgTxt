import sys
import pyperclip
from PIL import ImageGrab
from PyQt5 import QtCore, QtGui, QtWidgets
from pytesseract import pytesseract


class SnippingWidget(QtWidgets.QMainWindow):
    closed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(SnippingWidget, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("background:transparent;")
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        self.outsideSquareColor = "red"
        self.squareThickness = 2

        self.start_point = QtCore.QPoint()
        self.end_point = QtCore.QPoint()

    def mousePressEvent(self, event):
        self.start_point = event.pos()
        self.end_point = event.pos()
        self.update()
        print("press")

    def mouseMoveEvent(self, event):
        self.end_point = event.pos()
        self.update()
        print("move")

    def paintEvent(self, event):
        trans = QtGui.QColor(22, 100, 233)
        r = QtCore.QRectF(self.start_point, self.end_point).normalized()
        qp = QtGui.QPainter(self)
        trans.setAlphaF(0.2)
        qp.setBrush(trans)
        outer = QtGui.QPainterPath()
        outer.addRect(QtCore.QRectF(self.rect()))
        inner = QtGui.QPainterPath()
        inner.addRect(r)
        r_path = outer - inner
        qp.drawPath(r_path)
        qp.setPen(
            QtGui.QPen(QtGui.QColor(self.outsideSquareColor), self.squareThickness)
        )
        trans.setAlphaF(0)
        qp.setBrush(trans)
        qp.drawRect(r)
        print("event")

    def mouseReleaseEvent(self, QMouseEvent):
        r = QtCore.QRect(self.start_point, self.end_point).normalized()
        self.hide()

        #Работа со скрином
        img = ImageGrab.grab(bbox=r.getCoords())
        img.save("myPhoto/testImageX.png")

        # Определяем путь к бинарнику тессеракта
        path_to_tesseract = r"Tesseract-OCR\tesseract.exe"
        #tessdata_dir_config = r'"Tesseract-OCR\tessdata"'

        pytesseract.tesseract_cmd = path_to_tesseract

        # Преобразуем изображение в текст
        text = pytesseract.image_to_string(img, lang='rus')

        # Копирование текста в буфер
        pyperclip.copy(text)
        print(text)

        QtWidgets.QApplication.restoreOverrideCursor()

        # Переход на клозед
        self.closed.emit()

        self.start_point = QtCore.QPoint()
        self.end_point = QtCore.QPoint()
        print("release")


class MainWindow(QtWidgets.QMainWindow):
    #Функция выполняющаяся сразу после создания экземпляра класса
    def __init__(self):
        super().__init__()

        #Отрисовка мейна
        self.centralWidget = QtWidgets.QWidget()
        self.setCentralWidget(self.centralWidget)
        self.label = QtWidgets.QLabel(alignment=QtCore.Qt.AlignCenter)
        self.button = QtWidgets.QPushButton('Делать скриншот')
        self.snipper = SnippingWidget()

        layout = QtWidgets.QVBoxLayout(self.centralWidget)
        layout.addWidget(self.label, 1)
        layout.addWidget(self.button, 0)

        # Разрыв конекта со снипером
        self.snipper.closed.connect(self.on_closed)
        # При нажатии на кнопку активируется функция скриншотера
        self.button.clicked.connect(self.activateSnipping)

    def activateSnipping(self):
        #Растягиваем снипер на весь экран
        self.snipper.showFullScreen()
        #Меняем вид курсора
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)
        #?????
        self.hide()

    def on_closed(self):
        pixmap = QtGui.QPixmap("myPhoto/testImageX.png")
        self.label.setPixmap(pixmap)
        self.show()
        self.adjustSize()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.resize(400, 300)
    w.show()
    sys.exit(app.exec_())
