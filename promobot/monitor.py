import re
import socket
import time
import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime
from http.client import IncompleteRead
from json import dumps


class Monitor():
    timeout = 10
    config = {}
    data = {}
    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/35.0.1916.47 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,'
                  'application/xml;q=0.9,*/*;q=0.8'
    }

    def __init__(self, **kwargs):
        self.config.update({
            'proxies': kwargs.get('proxies'),
            'telegram': kwargs.get('telegram'),
        })

        self.config['telegram'].update({
            'chat_id': []
        })

        socket.setdefaulttimeout(self.timeout)

    def manage_chats(self, chats):
        config = self.config.get('telegram')
        add = list(
            set(chats) - set(config.get('chat_id'))
        )
        remove = list(
            set(config.get('chat_id')) - set(chats)
        )

        if add:
            config.get('chat_id').extend(add)

        for chat in remove:
            config.get('chat_id').remove(chat)

    def manage_keywords(self, keys):
        result = []
        add = list(
            set(keys) - set(self.data.keys())
        )
        remove = list(
            set(self.data.keys()) - set(keys)
        )

        for kw in add:
            self.data.update({
                kw.lower(): []
            })

        for kw in remove:
            self.data.pop(kw.lower())

        if add:
            action = 'Adding'
            result = add
        elif remove:
            action = 'Removing'
            result = remove

        if result:
            self.alert(
                'INFO',
                '{} keywords: {}'.format(
                    action,
                    result,
                )
            )

    def report(self, title, anchor):
        subs = self.config['telegram'].get('chat_id')

        for chat_id in subs:
            try:
                text = urllib.parse.urlencode({
                    'chat_id': chat_id,
                    'parse_mode': 'Markdown',
                    'text': 'Keyword: [{}]({})'.format(
                        title,
                        anchor,
                    ),
                }).encode()

                urllib.request.urlopen(
                    self.config['telegram']['url'],
                    text,
                )
            except (urllib.error.HTTPError, IncompleteRead, OSError) as e:
                self.alert(
                    'ERROR',
                    'Error on publishing data on telegram: {}'.format(
                        e
                    )
                )

    def alert(self, level, msg):
        print(
            '{} - {} - {}'.format(
                datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                level,
                msg,
            )
        )

        if level == 'ERROR':
            time.sleep(10)

    def lookup(self, kw, d, add):
        src = [
            d.get('url'),
            d.get('desc'),
        ]

        for text in src:
            if re.match(
                    r'.*{}.*'.format(kw),
                    str(text),
                    re.IGNORECASE,
            ):
                for v in self.data.get(kw):
                    if v.get('url') in d.get('url'):
                        add = False
                        break

                if add:
                    d.update({
                        'url': re.sub(
                            r'(\?)(?!.*\1).*$',
                            '',
                            d.get('url')
                        ),
                        'datetime': datetime.now().strftime(
                            '%d-%m-%Y %H:%M'
                        )
                    })

                    self.data[kw].append(
                        d
                    )

                    self.report(
                        kw,
                        d.get('url'),
                    )

                break

    def mount(self, src, each, t_title):
        desc = each.get('title')
        title = t_title.find(text=True)
        url = t_title.get('href')

        if src.get('desc'):
            desc = each.find(
                src['desc'].get('tag'),
                {
                    'class': src['desc'].get('class'),
                }
            )

            if desc:
                desc = desc.get_text()
            else:
                desc = ''

        if 'http' not in url:
            url = '{}/{}'.format(
                re.search(
                    r'.*://[^/]+',
                    src.get('url'),
                ).group(),
                url,
            )

        return {
            'title': re.sub(r'\n|\t', '', title),
            'desc': re.sub(r'\n|\t', '', desc),
            'url': url,
        }

    def get_topic(self, src):
        content = ''
        topic = []

        while len(topic) == 0:
            try:
                req = urllib.request.Request(
                    url=src['url'],
                    headers=self.header
                )

                content = urllib.request.urlopen(
                    req,
                ).read()
            except (urllib.error.HTTPError, IncompleteRead, OSError) as e:
                content = ''

                self.alert(
                    'ERROR',
                    'Error on getting data: {}'.format(
                        e,
                    )
                )

            if content:
                soup = BeautifulSoup(content, 'html.parser')

                if src['topic'].get('class'):
                    topic = soup.findAll(
                        src['topic']['tag'],
                        {'class': src['topic']['class']}
                    )
                else:
                    topic = soup.findAll(
                        src['topic']['tag']
                    )

                if len(topic) == 0:
                    self.alert(
                        'ERROR', 'Error on searching topics'
                    )

        return topic

    def main(self, src):
        topic = self.get_topic(src)

        for kw in self.data.keys():
            add = True

            for each in topic:
                if src['thread'].get('class'):
                    t_title = each.find(
                        src['thread']['tag'],
                        {'class': src['thread']['class']}
                    )
                else:
                    t_title = each.find(
                        src['thread']['tag']
                    )

                if t_title:
                    d = self.mount(
                        src,
                        each,
                        t_title
                    )

                    self.lookup(
                        kw,
                        d,
                        add,
                    )

        self.alert(
            'DEBUG',
            'Data from {}\n{}\n(Response at {})'.format(
                src.get('url'),
                dumps(self.data, indent=2, ensure_ascii=False),
                datetime.now().strftime('%H:%M:%S'),
            )
        )
