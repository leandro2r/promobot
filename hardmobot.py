#!/bin/python3

import notify2
import re
import time
import urllib.request
from bs4 import BeautifulSoup
from config import Config
from datetime import datetime
from dbus import exceptions
from http.client import IncompleteRead
from json import dumps


class Hardmobot(Config):
    config = {}
    data = {}

    def __init__(self):
        self.config.update(
            Config().data
        )

        for kw in self.config['keywords']:
            if not self.data.get(kw):
                self.data.update({
                    kw.lower(): []
                })

    def alert(self, level='', msg=''):
        if type(msg) == dict:
            try:
                text = urllib.parse.urlencode({
                    'chat_id': self.config['telegram']['chat_id'],
                    'parse_mode': 'Markdown',
                    'text': 'Keyword: [{}]({})'.format(
                        level,
                        msg['url']
                    ),
                }).encode()

                req = urllib.request.urlopen(
                    self.config['telegram']['url'],
                    text,
                )
            except (urllib.error.HTTPError, IncompleteRead, OSError) as e:
                self.alert(
                    'ERROR',
                    'Error on publishing data on telegram (proxy {}): {}'.format(
                        self.config['proxies']['http'],
                        e
                    )
                )
                self.__init__()
                time.sleep(20)

            level = msg['title']
            msg = '{}\n---\n{}'.format(
                msg['desc'],
                msg['url'],
            )
        else:
            print(
                '[{}] {}'.format(
                    level,
                    msg,
                )
            )

        if level != 'INFO':
            try:
                notify2.init('alert')
                n = notify2.Notification(
                    level,
                    msg,
                )
                n.show()
            except (exceptions.DBusException) as e:
                print('[ERROR] Error on alert: {}'.format(e))

    def main(self):
        topic = []

        hdr = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }

        hm_url = re.search(
            r'.*://[^/]+',
            self.config['url'],
        ).group()

        while len(topic) == 0:
            try:
                req = urllib.request.Request(
                    url=self.config['url'],
                    headers=hdr
                )
                content = urllib.request.urlopen(req).read()

                soup = BeautifulSoup(content, 'html.parser')

                topic = soup.findAll(
                    'div',
                    {'class': 'threadinfo'}
                )
            except (urllib.error.HTTPError, IncompleteRead, OSError) as e:
                self.alert(
                    'ERROR',
                    'Error on getting data (proxy {}): {}'.format(
                        self.config['proxies']['http'],
                        e,
                    )
                )
                self.__init__()
                time.sleep(20)

            if len(topic) == 0:
                self.alert('ERROR', 'Error on searching topics')
                self.__init__()
                time.sleep(20)

        for kw in self.data.keys():
            add = True

            for each in topic:
                title = each.find(
                    'a',
                    {'class': 'title'}
                )

                url = '{}/{}'.format(
                    hm_url,
                    title.get('href').lower(),
                )

                if kw in url:
                    for p in list(self.data.values()):
                        for v in p:
                            if url == v['url']:
                                add = False
                                break

                    if add:
                        self.data[kw].append({
                            'title': title.find(text=True),
                            'desc': each.get('title').replace('\n', ''),
                            'url': url,
                            'datetime': datetime.now().strftime('%d-%m-%Y %H:%M')
                        })

                        self.alert(
                            kw,
                            self.data[kw][-1],
                        )

        return self.data

    def loop(self):
        while True:
            res = self.main()
            self.alert(
                'INFO',
                'Response at {}:\n{}\n\n'.format(
                    datetime.now().strftime('%H:%M'),
                    dumps(res, indent=2, ensure_ascii=False),
                )
            )
            time.sleep(20)


if __name__ == '__main__':
    Hardmobot().loop()
