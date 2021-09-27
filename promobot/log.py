if __package__ is None or __package__ == '':
    from config import Config
else:
    from promobot.config import Config

import time
from datetime import datetime


class Log():
    def __init__(self):
        config = Config().data.get('monitor')

        self.muted = config.get('muted')
        self.timeout = config.get('timeout')

    def alert(self, level, msg):
        if level != 'DEBUG' or self.muted:
            print(
                '{} - {} - {}'.format(
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    level,
                    msg,
                )
            )

        if level == 'ERROR':
            time.sleep(self.timeout)
