import numpy as np
import cv2
import Bot
from Bot import *


def main():
    bot = Liner(0, "COM5")

    while True:

        bot.ride()
        bot.show()

        key = cv2.waitKey(5)

        print(bot.sonicRead(10, 8))

        if key == ord('w'):
            bot.start(bot.B, 50)

        if key == ord('s'):
            bot.start(bot.B, -50)

        if key == ord('e'):
            bot.start(bot.B, 0)

        if key == ord('q'):
            break


if __name__ == "__main__":
    main()
