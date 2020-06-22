#!/bin/python3

if __package__ is None or __package__ == '':
    from config import Config
    from data import Data
    from promobot import Promobot
else:
    from promobot.config import Config
    from promobot.data import Data
    from promobot.promobot import Promobot

import time


def main():
    config = Config().data
    data = Data(
        config.get('db')
    )
    promobot = Promobot(
        proxies=config.get('proxies'),
        telegram=config.get('telegram'),
        urls=config.get('urls'),
    )

    data.set_inital_keywords()

    while True:
        keywords = data.get_keywords()
        promobot.manage_keywords(
            keywords
        )

        promobot.main()
        time.sleep(10)


if __name__ == '__main__':
    main()
