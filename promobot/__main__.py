#!/bin/python3

if __package__ is None or __package__ == '':
    from config import Config
    from data import Data
    from monitor import Monitor
else:
    from promobot.config import Config
    from promobot.data import Data
    from promobot.monitor import Monitor

import time


def main():
    config = Config().data

    data = Data(
        config.get('db')
    )

    data.add_keywords()

    promobot = Promobot(
        env=config.get('env'),
        proxies=config.get('proxies'),
        telegram=config.get('telegram'),
        urls=config.get('urls'),
    )

    while True:
        chats = data.list_chats()
        keywords = data.list_keywords()

        promobot.manage_chats(
            chats
        )
        promobot.manage_keywords(
            keywords
        )

        promobot.main()
        time.sleep(10)


if __name__ == '__main__':
    main()
