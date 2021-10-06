import time
from datetime import datetime


class Log():
    def __init__(self, **kwargs):
        self.muted = kwargs.get('muted')
        self.timeout = kwargs.get('timeout')

    def alert(self, level, msg):
        datetime_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if level != 'DEBUG' or self.muted:
            print(
                f'{datetime_now} - {level} - {msg}'
            )

        if level == 'ERROR':
            time.sleep(self.timeout)
