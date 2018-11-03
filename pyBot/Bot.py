import cv2
import numpy as np

import arduino
from arduino import Arduino


def getAvgInArea(mat: np.matrix, x_y: tuple, radius: int) -> float:
    x, y = x_y

    average = 0
    cnt = 0

    for h in range(x - radius, x + radius + 1):
        for w in range(y - radius, y + radius + 1):
            # if float(h - x) ** 2 + float(w - y) ** 2 <= float(radius) ** 2:
            average += mat[h][w]
            cnt += 1
            mat[h][w] = 255 - mat[h][w]

    return int(average / cnt)


class Motor:
    def __init__(self, main, rev):
        self.mainPin = main
        self.revPin = rev
        self.speed = 0


class Controller(Arduino):
    def __init__(self, port):
        Arduino.__init__(self, port)
        self.A = Motor(5, 4)
        self.B = Motor(6, 7)

    def start(self, motor, speed):
        if motor.speed == speed:
            return

        else:
            motor.speed = speed

        if speed > 0:
            direction = arduino.mode.HIGH
        else:
            direction = arduino.mode.LOW

        speed = abs(speed)

        self.digitalWrite(motor.revPin, direction)
        self.analogWrite(motor.mainPin, speed)


class Camera:
    def __init__(self, port):
        self.cap = cv2.VideoCapture(port)
        self.frame = None

    def read(self):
        ret, self.frame = self.cap.read()

    def __del__(self):
        self.cap.release()


class widgetNames:
    rgbImg = "rgb"
    grayImg = "gray"
    binImg = "binary"

    sizeTracks = "size"
    colorTracks = "color"
    robotControl = "coefficients"

    class coef:
        prop = "propotrional"
        cube = "cubic"
        integral = "integral"
        diff = "differencial"

        base = "base speed"

    class threshold:
        down = "down"
        high = "high"

    class Roi:
        x1 = "x1"
        y1 = "y1"

        x2 = "x2"
        y2 = "y2"

        scope = "size"


class GUIService:
    def __init__(self):
        self.camSize = (640, 480)

        self.x1 = 0
        self.x2 = self.camSize[0]
        self.y1 = 0
        self.y2 = self.camSize[1]

        self.down = 100
        self.high = 255

        self.prop = 0
        self.cube = 0
        self.diff = 0
        self.intg = 0

        self.base = 40

        self.scope = 1

        self.gray = None
        self.frame = None
        self.bin = None

        cv2.namedWindow(widgetNames.rgbImg)
        cv2.namedWindow(widgetNames.grayImg)
        cv2.namedWindow(widgetNames.binImg)

        cv2.namedWindow(widgetNames.colorTracks)
        cv2.namedWindow(widgetNames.sizeTracks)
        cv2.namedWindow(widgetNames.robotControl)

        cv2.createTrackbar(widgetNames.threshold.down, widgetNames.colorTracks, self.down, 255, self.onDown)
        cv2.createTrackbar(widgetNames.threshold.high, widgetNames.colorTracks, self.high, 255, self.onHigh)

        cv2.createTrackbar(widgetNames.Roi.x1, widgetNames.sizeTracks, self.x1, 640, self.onX1)
        cv2.createTrackbar(widgetNames.Roi.x2, widgetNames.sizeTracks, self.x2, 640, self.onX2)

        cv2.createTrackbar(widgetNames.Roi.y1, widgetNames.sizeTracks, self.y1, 480, self.onY1)
        cv2.createTrackbar(widgetNames.Roi.y2, widgetNames.sizeTracks, self.y2, 480, self.onY2)

        cv2.createTrackbar(widgetNames.coef.prop, widgetNames.robotControl, self.prop, 200, self.onProp)
        cv2.createTrackbar(widgetNames.coef.cube, widgetNames.robotControl, self.cube, 200, self.onCube)
        cv2.createTrackbar(widgetNames.coef.diff, widgetNames.robotControl, self.diff, 200, self.onDiff)
        cv2.createTrackbar(widgetNames.coef.integral, widgetNames.robotControl, self.intg, 200, self.onIntg)
        cv2.createTrackbar(widgetNames.coef.base, widgetNames.robotControl, self.base, 200, self.onBase)

        cv2.createTrackbar(widgetNames.Roi.scope, widgetNames.sizeTracks, self.scope, 10, self.onScope)
        cv2.setTrackbarMin(widgetNames.Roi.scope, widgetNames.sizeTracks, 1)

    def show(self):
        cv2.imshow(widgetNames.rgbImg, self.frame)
        cv2.imshow(widgetNames.grayImg, self.gray)
        cv2.imshow(widgetNames.binImg, self.bin)

    def onX1(self, val):
        self.x1 = val

    def onX2(self, val):
        self.x2 = val

    def onY1(self, val):
        self.y1 = val

    def onY2(self, val):
        self.y2 = val

    def onDown(self, val):
        self.down = val

    def onHigh(self, val):
        self.high = val

    def onProp(self, val):
        self.prop = val

    def onCube(self, val):
        self.cube = val

    def onDiff(self, val):
        self.diff = val

    def onIntg(self, val):
        self.intg = val

    def onBase(self, val):
        self.base = val

    def onScope(self, val):
        self.scope = val

        self.x1 = 0
        self.y1 = 0
        self.x2 = self.camSize[0] // self.scope
        self.y2 = self.camSize[1] // self.scope

        cv2.setTrackbarPos(widgetNames.Roi.x1, widgetNames.sizeTracks, 0)
        cv2.setTrackbarPos(widgetNames.Roi.y1, widgetNames.sizeTracks, 0)

        cv2.setTrackbarMax(widgetNames.Roi.x2, widgetNames.sizeTracks, self.x2)
        cv2.setTrackbarMax(widgetNames.Roi.y2, widgetNames.sizeTracks, self.y2)

        cv2.setTrackbarPos(widgetNames.Roi.x2, widgetNames.sizeTracks, self.x2)
        cv2.setTrackbarPos(widgetNames.Roi.y2, widgetNames.sizeTracks, self.y2)


class ImageLogic(Camera, GUIService):
    def __init__(self, port):
        Camera.__init__(self, port)
        GUIService.__init__(self)

        self.size = (640, 480)

        self.gray = None
        self.bin = None

        self.contours = None

    def makeImage(self):
        self.read()
        self.frame = cv2.resize(self.frame, (self.size[0] // self.scope, self.size[1] // self.scope))

        self.frame = self.frame[self.y1:self.y2, self.x1: self.x2]

        self.frame = cv2.blur(self.frame, (3, 3))

        self.gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

        ret, self.bin = cv2.threshold(self.gray, self.down, self.high, cv2.THRESH_BINARY)

        ret, self.contours, hierarchy = cv2.findContours(self.bin, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # cv2.drawContours(self.frame, contours, -1, (0, 0, 255), 2)

    def findLine(self) -> int:
        avg = 0
        cnt = 0
        for cont in self.contours:
            for dot in cont:
                x, y = dot[0]
                cv2.circle(self.frame, (x, y), 4, (0, 255, 0), -1)
                avg += x
                cnt += 1

        lineX = int(avg / cnt)
        cv2.circle(self.frame, (lineX, 120), 5, (255, 0, 0), -1)

        return lineX


class Liner(ImageLogic, Controller):
    def __init__(self, camPort, ardPort):
        ImageLogic.__init__(self, camPort)
        Controller.__init__(self, ardPort)

        self.oldErr = 0
        self.integralValue = 0
        self.automate = False

    def ride(self):
        self.makeImage()

        line = self.findLine()

        speed = line * self.prop \
                + line * self.cube

        if self.automate == True:
            self.start(self.A, self.base + speed)
            self.start(self.B, self.base - speed)