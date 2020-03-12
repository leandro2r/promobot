#!/bin/python3

if __package__ is None or __package__ == '':
    from promobot import Promobot
else:
    from promobot.promobot import Promobot

import time


def main():
    promobot = Promobot()

    while True:
        promobot.main()
        time.sleep(10)


if __name__ == '__main__':
    main()
