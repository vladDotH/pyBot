import numpy as np
import cv2
from pyBot.lineBot import *


def main():
    # bot = Bot(0)

    vision = ImageLogic(0)

    while True:

        # bot.ride()
        # bot.show()

        vision.makeImage()

        # line = vision.findLine() - abs(vision.x1 - vision.x2) // 2
        vision.show()


        key = cv2.waitKey(5)

        # if key == ord('w'):
        #     bot.move(100, 100)
        #
        # elif key == ord('s'):
        #     bot.move(-100, -100)
        #
        # elif key == ord('e'):
        #     bot.move(0, 0)
        #
        if key == ord('q'):
            break
        #
        # else:
        #     bot.move(0, 0)


if __name__ == "__main__":
    main()
