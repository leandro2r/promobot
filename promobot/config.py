import base64
import os
import random
import re
from datetime import datetime


class Config():
    data = {
        'db': {},
        'proxies': {
            'http': '',
            'https': ''
        },
        'telegram': {},
        'urls': [],
    }

    def __init__(self):
        self.set_proxy()

        self.data['urls'].extend([
            {
                'url': 'http://www.hardmob.com.br/forums/407-Promocoes'
                       '?s=&pp=50&daysprune=1&sort=dateline&order=desc',
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

        self.data['db'].update({
            'host': os.environ.get('DB_HOST', 'localhost:27017'),
            'user': os.environ.get('MONGO_INITDB_ROOT_USERNAME'),
            'passwd': os.environ.get('MONGO_INITDB_ROOT_PASSWORD'),
            'client': os.environ.get(
                'MONGO_INITDB_DATABASE',
                'promobot'
            ),
        })

        self.data['telegram'].update({
            'token': os.environ.get(
                'TELEGRAM_TOKEN',
                ''
            ),
            'chat_passwd': os.environ.get('TELEGRAM_CHAT_PASSWD', '')
        })

        self.data['telegram'].update({
            'url': 'https://api.telegram.org/bot{}/sendMessage'.format(
                self.data['telegram']['token']
            )
        })

    def set_proxy(self):
        ip = ''
        ips = []
        proxy_file = '/etc/environment'

        proxy_enabled = eval(
            os.environ.get('PROXY_ENABLED', 'False').title()
        )

        if not proxy_enabled:
            if "HTTP_PROXY" in os.environ:
                del os.environ['HTTP_PROXY']

            if "HTTPS_PROXY" in os.environ:
                del os.environ['HTTPS_PROXY']

            return

        if ips:
            ip = random.choice(ips)

        elif os.path.exists(proxy_file):
            with open(proxy_file, 'r') as f:
                get_proxy = re.search(r'http://\S+', f.read())
                f.close()

                ip = get_proxy.group()

        print(
            '{} - {} - Setting proxy: {}'.format(
                datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'INFO',
                ip,
            )
        )

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

        self.data['proxies'].update({
            'http': os.environ.get('HTTP_PROXY'),
            'https': os.environ.get('HTTPS_PROXY')
        })
