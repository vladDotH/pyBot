import threading
import time

import cv2
import numpy as np


# import RPi.GPIO as GPIO

# !!!
# GPIO.setmode(GPIO.BOARD)


def limit(_min, _max, val):
    return min(_max, max(_min, val))


class Motor:
    def __init__(self, speed_pin, dir1, dir2):
        self.dir1 = dir1
        self.dir2 = dir2
        self.speed_pin = speed_pin
        self.speed = 0

        _ = [
            GPIO.setup(i, GPIO.OUT) for i in [speed_pin, dir1, dir2]
        ]

        self.speed_pwm = GPIO.PWM(speed_pin, 1024)

    def start(self, speed):
        speed = limit(-100, 100, speed)

        if speed == self.speed:
            return

        self.speed = speed

        if speed > 0:
            GPIO.output(self.dir1, GPIO.HIGH)
            GPIO.output(self.dir2, GPIO.LOW)

        if speed < 0:
            GPIO.output(self.dir1, GPIO.LOW)
            GPIO.output(self.dir2, GPIO.HIGH)

        if speed == 0:
            GPIO.output(self.dir1, GPIO.LOW)
            GPIO.output(self.dir2, GPIO.LOW)

        self.speed_pwm.start(abs(speed))


class Bot:
    def __init__(self, left_motor, right_motor):
        self.left = Motor(*left_motor)
        self.right = Motor(*right_motor)

    def move(self, l, r):
        self.left.start(l)
        self.right.start(r)

    def __del__(self):
        self.move(0, 0)
        self.close()

    def close(self):
        GPIO.cleanup()


class Camera:
    def __init__(self, port):
        self.cap = cv2.VideoCapture(port)
        self.frame = None

    def read(self):
        ret, self.frame = self.cap.read()

    def __del__(self):
        self.cap.release()


class widgetNames:
    frameImg = "frame"
    rgbImg = "rgb"
    grayImg = "gray"
    binImgB = "binary1"
    binImgW = "binary2"

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
        self.scope = 2
        self.camSize = (640 // self.scope, 480 // self.scope)

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

        self.frame = None
        self.image = None
        self.gray = None
        self.binB = None
        self.binW = None

        cv2.namedWindow(widgetNames.frameImg)
        cv2.namedWindow(widgetNames.rgbImg)
        cv2.namedWindow(widgetNames.grayImg)
        cv2.namedWindow(widgetNames.binImgB)
        cv2.namedWindow(widgetNames.binImgW)

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

        # self.onScope(self.scope)

    def show(self):
        cv2.imshow(widgetNames.frameImg, self.frame)
        cv2.imshow(widgetNames.rgbImg, self.image)
        cv2.imshow(widgetNames.grayImg, self.gray)
        cv2.imshow(widgetNames.binImgB, self.binB)
        cv2.imshow(widgetNames.binImgW, self.binW)

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

        cv2.setTrackbarMax(widgetNames.Roi.x1, widgetNames.sizeTracks, self.x2)
        cv2.setTrackbarMax(widgetNames.Roi.y1, widgetNames.sizeTracks, self.y2)

        cv2.setTrackbarMax(widgetNames.Roi.x2, widgetNames.sizeTracks, self.x2)
        cv2.setTrackbarMax(widgetNames.Roi.y2, widgetNames.sizeTracks, self.y2)

        cv2.setTrackbarPos(widgetNames.Roi.x1, widgetNames.sizeTracks, 0)
        cv2.setTrackbarPos(widgetNames.Roi.y1, widgetNames.sizeTracks, 0)

        cv2.setTrackbarPos(widgetNames.Roi.x2, widgetNames.sizeTracks, self.x2)
        cv2.setTrackbarPos(widgetNames.Roi.y2, widgetNames.sizeTracks, self.y2)


class ImageLogic(Camera, GUIService):
    def __init__(self, port):
        Camera.__init__(self, port)
        GUIService.__init__(self)

        self.size = (640, 480)

        self.image = None
        self.gray = None
        self.binB = None
        self.binW = None

        self.contours = None

    def makeImage(self):
        self.read()
        self.frame = cv2.resize(self.frame, (self.size[0] // self.scope, self.size[1] // self.scope))

        self.image = self.frame[self.y1:self.y2, self.x1: self.x2]

        self.image = cv2.blur(self.image, (3, 3))

        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

        ret, self.binB = cv2.threshold(self.gray, self.down, self.high, cv2.THRESH_BINARY_INV)
        ret, self.binW = cv2.threshold(self.gray, self.down, self.high, cv2.THRESH_BINARY)

        self.mB = cv2.moments(self.binB)
        self.mW = cv2.moments(self.binW)

        self.areaB = self.mB['m00']
        self.areaW = self.mW['m00']

        if self.areaB > self.areaW:
            self.X = self.mW['m10']
            self.Y = self.mW['m01']
            self.area = self.mW['m00']

        else:
            self.X = self.mB['m10']
            self.Y = self.mB['m01']
            self.area = self.mB['m00']


        if self.area > 0:
            self.x = self.X / self.area
            self.y = self.Y / self.area
            cv2.circle(self.image, (int(self.x), int(self.y)), 5, (255, 0, 255))

        # ret, self.contours, hierarchy = cv2.findContours(self.bin, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # cv2.drawContours(self.frame, contours, -1, (0, 0, 255), 2)

        cv2.rectangle(self.frame, (self.x1, self.y1), (self.x2, self.y2), (0, 255, 255), 1)

    def findLine(self) -> int:
        # avg = 0
        # cnt = 1
        # for cont in self.contours:
        #     for dot in cont:
        #         x, y = dot[0]
        #         cv2.circle(self.image, (x, y), 4, (0, 255, 0), -1)
        #         avg += x
        #         cnt += 1
        #
        # lineX = int(avg / cnt)
        # cv2.circle(self.image, (lineX, 120), 5, (255, 0, 0), -1)
        pass
        # return lineX


class Liner(ImageLogic, Bot):
    def __init__(self, camPort, lm, rm):
        ImageLogic.__init__(self, camPort)
        Bot.__init__(self, lm, rm)

        self.oldErr = 0
        self.integralValue = 0
        self.automate = False

    def ride(self):
        self.makeImage()

        line = self.findLine() - abs(self.x1 - self.x2) // 2

        # print(line)

        speed = line * self.prop / 100 \
                + line * self.cube / 10000

        if self.automate == True:
            self.start(self.A, self.base + speed)
            self.start(self.B, self.base - speed)
