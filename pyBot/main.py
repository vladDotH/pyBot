import numpy as np
import cv2
import Bot
from Bot import *


def main():
    bot = Liner(0, "COM1")

    while True:

        bot.ride()
        bot.show()

        key = cv2.waitKey(1)

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
