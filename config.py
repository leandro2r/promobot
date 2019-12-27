import os
import re

class Config():
    data = {
        'url': {
            'hardmob': '',
            'pelando': ''
        },
        'keywords': [],
        'proxies': {
            'http': '',
            'https': ''
        },
        'telegram': {},
    }

    def check_proxy(self):
        ip = ''
        proxy_file = '/etc/environment'

        if os.path.exists(proxy_file):
            with open(proxy_file, 'r') as f:
                get_proxy = re.search(r'http://\S+', f.read())
                f.close()

                ip = get_proxy.group()

        print('[INFO] Getting proxy: {}'.format(ip))

        return ip

    def __init__(self):
        proxy = self.check_proxy()

        self.data['proxies'].update({
            'http': os.environ.get('HTTP_PROXY', proxy),
            'https': os.environ.get('HTTPS_PROXY', proxy)
        })

        if 'HTTP_PROXY' or 'HTTPS_PROXY' in os.environ and proxy:
            os.environ['HTTP_PROXY'] = proxy
            os.environ['HTTPS_PROXY'] = proxy

        self.data['url'] = {
            'hardmob': os.environ.get(
                'HARDMOB_URL',
                'http://www.hardmob.com.br/forums/407-Promocoes?s=&pp=50&daysprune=1&sort=dateline&order=desc'
            ),
            'pelando': os.environ.get(
                'PELANDO_URL',
                'https://www.pelando.com.br/recentes'
            )
        }

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
