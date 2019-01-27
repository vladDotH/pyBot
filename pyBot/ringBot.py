import threading
import time

import cv2
import numpy as np

from pyBot import arduino
from pyBot.arduino import Arduino


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

        self.pinMode(4, arduino.mode.OUT)
        self.pinMode(5, arduino.mode.OUT)
        self.pinMode(6, arduino.mode.OUT)
        self.pinMode(7, arduino.mode.OUT)

        self.USListenerAlive = False
        self.sleepTime = 0.05
        self.USData = None

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

    def sonicListenerStart(self, trig, echo):
        if not self.USListenerAlive:
            self.USListenerAlive = True

            def sonicListenerThread():
                while self.USListenerAlive:
                    # time.sleep(self.sleepTime)
                    threading.Event().wait(0.1)

                    self.USData = self.sonicRead(trig, echo)

                    # print("readed : ", self.USData)

            usThread = threading.Thread(target=sonicListenerThread)
            usThread.start()


class Camera:
    def __init__(self, port, size):
        self.cap = cv2.VideoCapture(port)

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, size[0] )
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, size[1])

        self.frame = None

    def read(self):
        ret, self.frame = self.cap.read()

    def __del__(self):
        self.cap.release()


class widgetNames:
    grayImg = "gray"

    sizeTracks = "size"
    robotControl = "coefficients"

    class coef:
        prop = "propotrional"
        cube = "cubic"
        integral = "integral"
        diff = "differencial"

        base = "base speed"


class GUIService:
    def __init__(self):

        self.prop = 0
        self.cube = 0
        self.diff = 0
        self.intg = 0

        self.base = 40

        self.gray = None

        cv2.namedWindow(widgetNames.grayImg)

        cv2.namedWindow(widgetNames.sizeTracks)
        cv2.namedWindow(widgetNames.robotControl)


        cv2.createTrackbar(widgetNames.coef.prop, widgetNames.robotControl, self.prop, 200, self.onProp)
        cv2.createTrackbar(widgetNames.coef.cube, widgetNames.robotControl, self.cube, 200, self.onCube)
        cv2.createTrackbar(widgetNames.coef.diff, widgetNames.robotControl, self.diff, 200, self.onDiff)
        cv2.createTrackbar(widgetNames.coef.integral, widgetNames.robotControl, self.intg, 200, self.onIntg)
        cv2.createTrackbar(widgetNames.coef.base, widgetNames.robotControl, self.base, 200, self.onBase)


    def show(self):
        cv2.imshow(widgetNames.grayImg, self.gray)

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


class ImageLogic(Camera, GUIService):
    def __init__(self, port):
        Camera.__init__(self, port)
        GUIService.__init__(self)

        self.gray = None

    def makeImage(self):
        self.read()
        self.frame = cv2.resize(self.frame, (self.size[0] // self.scope, self.size[1] // self.scope))

        self.image = self.frame

        self.image = cv2.blur(self.image, (3, 3))

        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)


class Liner(ImageLogic, Controller):
    def __init__(self, camPort, ardPort):
        ImageLogic.__init__(self, camPort)
        Controller.__init__(self, ardPort)

        self.oldErr = 0
        self.integralValue = 0
        self.automate = False
