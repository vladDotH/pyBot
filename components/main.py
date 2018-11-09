import cv2
import numpy
import sys

sys.setrecursionlimit(1000000)


def markComponentsRecursion(mat: numpy.matrix, startPoint: tuple):
    h, w, channels = mat.shape

    x, y = startPoint
    color = tuple(mat[y][x])

    byteField = numpy.zeros((h, w))

    def recure(point):
        x, y = point

        current = mat[y][x]
        # print('in', byteField[x][y], color)

        if byteField[x][y] == 0 \
                and abs(int(color[0]) - int(current[0])) < 20 \
                and abs(int(color[1]) - int(current[1])) < 20 \
                and abs(int(color[2]) - int(current[2])) < 20:
            byteField[x][y] = 1
            mat[y][x] = (0, 0, 0)

            cv2.imshow("__", mat)

            recure((x - 1, y - 1))
            recure((x, y - 1))
            recure((x + 1, y - 1))

            recure((x - 1, y))
            recure((x + 1, y))

            recure((x - 1, y + 1))
            recure((x, y + 1))
            recure((x + 1, y + 1))

    recure(startPoint)

    cv2.imshow("__", mat)


def markComponentsCycle(mat: numpy.matrix, startPoint: tuple):
    h, w, channels = mat.shape

    x, y = startPoint
    color = tuple(mat[y][x])

    byteField = numpy.zeros((w, h))

    stack = [ startPoint ]

    while len(stack) != 0:
        x, y = stack.pop()

        if x < w and y < h and x >= 0 and y >= 0:
            current = mat[y][x]

            # cv2.imshow("__", mat)
            # cv2.waitKey(1)

            if byteField[x][y] == 0 \
                    and abs(int(color[0]) - int(current[0])) < 20 \
                    and abs(int(color[1]) - int(current[1])) < 20 \
                    and abs(int(color[2]) - int(current[2])) < 20:
                byteField[x][y] = 1
                mat[y][x] = (0, 0, 0)

                stack.append((x - 1, y - 1))
                stack.append((x, y - 1))
                stack.append((x + 1, y - 1))

                stack.append((x - 1, y))
                stack.append((x + 1, y))

                stack.append((x - 1, y + 1))
                stack.append((x, y + 1))
                stack.append((x + 1, y + 1))


    cv2.imshow("__", mat)

img: numpy.matrix = None


def knowColor(event, x, y, flags, data):
    if event == cv2.EVENT_LBUTTONDOWN:
        # print( x, y )
        # print(img[y][x])
        markComponentsCycle(img, (x, y))


cv2.namedWindow("window")
cv2.setMouseCallback("window", knowColor)

img = cv2.imread("C:/Users/KK/PycharmProjects/pyson/example2.jpg")

cv2.imshow("window", img)
cv2.waitKey(0)
