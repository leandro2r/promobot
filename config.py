import base64
import os
import random
import re


class Config():
    data = {
        'keywords': [],
        'proxies': {
            'http': '',
            'https': ''
        },
        'telegram': {},
        'src': [],
    }

    def set_proxy(self):
        ip = ''
        ips = []
        proxy_file = '/etc/environment'

        if ips:
            ip = random.choice(ips)

        elif os.path.exists(proxy_file):
            with open(proxy_file, 'r') as f:
                get_proxy = re.search(r'http://\S+', f.read())
                f.close()

                ip = get_proxy.group()

        print('[INFO] Setting proxy: {}'.format(ip))

        ip_auth = ip.replace(
            'http://',
            'http://{}'.format(
                base64.b64decode(
                    os.environ.get('AUTH_PROXY', '')
                ).decode('utf-8').strip()
            )
        )

        os.environ['HTTP_PROXY'] = ip_auth
        os.environ['HTTPS_PROXY'] = ip_auth

    def __init__(self):
        self.set_proxy()

        self.data['proxies'].update({
            'http': os.environ.get('HTTP_PROXY'),
            'https': os.environ.get('HTTPS_PROXY')
        })

        self.data['src'].extend([
            {
                'url': 'http://www.hardmob.com.br/forums/407-Promocoes?s=&pp=50&daysprune=1&sort=dateline&order=desc',
                'topic': {
                    'tag': 'div',
                    'class': 'threadinfo'
                },
                'thread': {
                    'tag': 'a',
                    'class': 'title'
                }
            },
            {
                'url': 'https://www.pelando.com.br/recentes',
                'topic': {
                    'tag': 'article',
                    'class': ''
                },
                'thread': {
                    'tag': 'a',
                    'class': 'cept-tt thread-link linkPlain thread-title--card'
                }
            }
        ])

        self.data['keywords'] = os.environ['KEYWORDS'].split(';')

        self.data['telegram'].update({
            'token': os.environ.get(
                'TOKEN',
                '',
            ),
            'chat_id': os.environ.get('CHAT_ID', '')
        })

        self.data['telegram']['url'] = 'https://api.telegram.org/bot{}/sendMessage'.format(
            self.data['telegram']['token']
        )

        print(
            '[INFO] Setting keywords: {}'.format(
                self.data['keywords'],
            )
        )
