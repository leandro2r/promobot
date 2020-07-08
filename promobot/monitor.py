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
        result = []
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
            print(
                '{} - {} - {} keywords: {}'.format(
                    datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                    'INFO',
                    action,
                    result,
                )
            )

    def alert(self, level='', msg=''):
        if isinstance(msg, dict):
            if self.config['telegram'].get('token'):
                for chat_id in self.config['telegram'].get('chat_id'):
                    try:
                        text = urllib.parse.urlencode({
                            'chat_id': chat_id,
                            'parse_mode': 'Markdown',
                            'text': 'Keyword: [{}]({})'.format(
                                level,
                                msg['url']
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

            level = msg['title']
            msg = '{}\n---\n{}'.format(
                msg['desc'],
                msg['url'],
            )
        else:
            print(
                '{} - {} - {}'.format(
                    datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                    level,
                    msg,
                )
            )

        if level == 'ERROR':
            time.sleep(10)

    def add_thread(self, kw, add, title, desc, url):
        if title:
            title = re.sub(r'\n|\t', '', title)

        if desc:
            desc = re.sub(r'\n|\t', '', desc)

        if re.match(
                r'.*{}.*'.format(kw),
                url
           ):
            for p in list(self.data.values()):
                for v in p:
                    if v['url'] in url:
                        add = False
                        break

            if add:
                self.data[kw].append({
                    'title': title,
                    'desc': desc,
                    'url': re.sub(r'(\?)(?!.*\1).*$', '', url),
                    'datetime': datetime.now().strftime('%d-%m-%Y %H:%M')
                })

                self.alert(
                    kw,
                    self.data[kw][-1],
                )

    def pelando(self, each, t_title):
        d = {}
        d['title'] = t_title.find(text=True)
        d['desc'] = each.find(
            'div',
            {
                'class': 'cept-description-container overflow--wrap-break '
                         'width--all-12  size--all-s size--fromW3-m'
            }
        )
        d['url'] = t_title.get('href').lower()
        return d

    def gatry(self, each, t_title):
        d = {}
        d['title'] = t_title.find(text=True)
        d['desc'] = each.find(
            'p',
            {
                'class': 'preco comentario clear'
            }
        )
        d['url'] = t_title.get('href').lower()

        if d['desc']:
            d['desc'] = d['desc'].get_text()

        return d

    def hardmob(self, each, t_title, url):
        d = {}
        d['title'] = t_title.find(text=True)
        d['desc'] = each.get('title')
        d['url'] = '{}/{}'.format(
            re.search(
                r'.*://[^/]+',
                url,
            ).group(),
            t_title.get('href').lower(),
        )
        return d

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
                    t = {}

                    if 'hardmob' in src['url']:
                        t = self.hardmob(each, t_title, src['url'])
                    elif 'pelando' in src['url']:
                        t = self.pelando(each, t_title)
                    elif 'gatry' in src['url']:
                        t = self.gatry(each, t_title)

                    self.add_thread(kw, add, t['title'], t['desc'], t['url'])

        self.alert(
            'DEBUG',
            'Data from {}\n{}\n(Response at {})'.format(
                src.get('url'),
                dumps(self.data, indent=2, ensure_ascii=False),
                datetime.now().strftime('%H:%M:%S'),
            )
        )
