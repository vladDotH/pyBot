import numpy as np
import cv2
import Bot
from Bot import *


def main():
    bot = Liner(0, "COM5")

    bot.sonicListenerStart(10, 8)

    while True:

        bot.ride()
        bot.show()

        key = cv2.waitKey(5)

        print(bot.USData)

        if key == ord('w'):
            bot.start(bot.B, 150)
            bot.start(bot.A, -150)

        elif key == ord('s'):
            bot.start(bot.B, -100)
            bot.start(bot.A, 100)

        elif key == ord('e'):
            bot.start(bot.B, 0)
            bot.start(bot.A, 0)

        elif key == ord('q'):
            break

        else:
            bot.start(bot.A, 0)
            bot.start(bot.B, 0)


    bot.start(bot.B, 0)
    bot.start(bot.A, 0)

    bot.USListenerAlive = False


if __name__ == "__main__":
    main()
