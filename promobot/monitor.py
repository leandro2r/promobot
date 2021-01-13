import re
import threading
import time
import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from http.client import IncompleteRead
from json import dumps


class Monitor():
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
            'monitor': kwargs.get('monitor'),
            'proxies': kwargs.get('proxies'),
            'telegram': kwargs.get('telegram'),
        })

        self.config['telegram'].update({
            'chat_id': []
        })

    def manage_config(self, configs):
        for d in configs:
            if d.get('delay'):
                self.config['monitor'].update({
                    'delay': int(d.get('delay'))
                })

            if d.get('reset'):
                self.config['monitor'].update({
                    'reset': int(d.get('reset'))
                })

            if d.get('timeout'):
                self.config['monitor'].update({
                    'timeout': int(d.get('timeout'))
                })

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
                kw: []
            })

        for kw in remove:
            self.data.pop(kw)

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
        subs = self.config['telegram'].get('chat_id', [])

        if self.config['monitor']['muted']:
            subs = []

        for chat_id in subs:
            try:
                text = urllib.parse.urlencode({
                    'chat_id': chat_id,
                    'parse_mode': 'Markdown',
                    'text': 'Keyword: **[{}]({})**'.format(
                        title,
                        anchor,
                    ),
                }).encode()

                urllib.request.urlopen(
                    self.config['telegram']['url'],
                    text,
                    timeout=self.config['monitor']['timeout'],
                )
            except (urllib.error.HTTPError, IncompleteRead, OSError) as e:
                self.alert(
                    'ERROR',
                    'Error on publishing data on telegram: {}'.format(
                        e
                    )
                )

    def alert(self, level, msg):
        if level != 'DEBUG' or self.config['monitor']['muted']:
            print(
                '{} - {} - {}'.format(
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    level,
                    msg,
                )
            )

        if level == 'ERROR':
            time.sleep(self.config['monitor']['timeout'])

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
        desc = each.get('title', '')
        title = t_title.find(text=True)
        url = t_title.get('href', '')

        if src.get('desc'):
            desc = each.find(
                src['desc'].get('tag'),
                {
                    'class': src['desc'].get('class'),
                }
            )

            try:
                if desc.get_text():
                    desc = desc.get_text()
                else:
                    desc = desc.find().get(
                        'title',
                        desc
                    )
            except Exception:
                desc = ''

        if not isinstance(title, str):
            content = re.search(
                r'[^/]+$',
                url
            ).group()

            title = re.sub(
                '-+',
                ' ',
                content
            ).title()

        if 'http' not in url:
            domain = re.search(
                r'.*://[^/?]+',
                src.get('url'),
            ).group()

            url = '{}/{}'.format(
                domain,
                re.sub(r'^/', '', url),
            )

        return {
            'title': re.sub(r'\n|\t', '', str(title)),
            'desc': re.sub(r'\n|\t', '', str(desc)),
            'url': str(url),
        }

    def get_promo(self, src):
        content = ''
        topic = []

        while len(topic) == 0:
            try:
                req = urllib.request.Request(
                    url=src.get('url'),
                    headers=self.header
                )

                content = urllib.request.urlopen(
                    req,
                    timeout=self.config['monitor']['timeout'],
                ).read()

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
                            'ERROR',
                            'Error on searching topics in {}: {}'.format(
                                src.get('url'),
                                str(soup)[:10]
                            )
                        )
            except (urllib.error.HTTPError, IncompleteRead, OSError) as e:
                self.alert(
                    'ERROR',
                    'Error on getting data from {}: {}'.format(
                        src.get('url'),
                        e,
                    )
                )

        return topic

    def monitor(self, src):
        promo = self.get_promo(src)

        for kw in self.data.keys():
            add = True

            for each in promo:
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
            '\n{}'.format(
                dumps(self.data, indent=2, ensure_ascii=False),
            )
        )

        self.alert(
            'INFO',
            'Last lookup from {}'.format(
                src.get('url'),
            )
        )

    def reset_old(self, hours):
        for k, v in self.data.items():
            for i in range(len(v)):
                list_v = self.data[k]
                old = (
                    datetime.now() - timedelta(hours=hours)
                ).strftime('%d-%m-%Y %H:%M')

                if i < len(v):
                    try:
                        if list_v[i]['datetime'] <= old:
                            self.alert(
                                'INFO',
                                (
                                    'Reseting {}º {} '
                                    'value from {}'
                                ).format(
                                    i + 1,
                                    k,
                                    list_v[i]['datetime'],
                                )
                            )
                            del list_v[i]
                    except IndexError:
                        pass

    def runner(self, data, url):
        runtime = 0

        while True:
            config = data.list_config()
            chats = data.list_chats()
            keywords = data.list_keywords()

            self.manage_config(
                config
            )
            self.manage_chats(
                chats
            )
            self.manage_keywords(
                keywords
            )

            self.monitor(url)

            delay = self.config['monitor']['delay']
            reset = self.config['monitor']['reset']

            time.sleep(delay)
            runtime += delay

            if runtime >= reset * 3600 / 2:
                self.reset_old(reset)
                runtime = 0

    def main(self, data, urls):
        proc = []

        for i in range(len(urls)):
            m = threading.Thread(
                target=self.runner,
                args=(
                    data,
                    urls[i],
                )
            )
            proc.append(m)

        for p in proc:
            p.start()

        for p in proc:
            p.join()
