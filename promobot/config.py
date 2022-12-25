import base64
import os
import random
import re
import yaml


class Config():
    data = {
        'proxies': {
            'http': '',
            'https': ''
        }
    }

    def __init__(self, **kwargs):
        config_file = os.environ.get('CONFIG', '/etc/promobot/promobot.yml')

        region = kwargs.get('region', 'br')
        urls = kwargs.get('urls')
        refs = {}

        with open(config_file, 'r') as file:
            try:
                data = yaml.safe_load(file)
                if data['promobot'].get('config'):
                    refs = data['promobot']['config'].get('refs', {})
            except yaml.YAMLError as error:
                print(f'Error reading {config_file}: {error}')

        if not refs:
            print(
                (
                    f'Empty promobot.config.refs.{region} '
                    f'data on {config_file}.'
                )
            )

        self.set_proxy()

        self.data['monitor'] = {
            'delay': int(os.environ.get('DELAY', 40)),
            'muted': bool(os.environ.get('MUTED', 'false') == 'true'),
            'reset': int(os.environ.get('RESET_TIME', 72)),
            'timeout': int(os.environ.get('TIMEOUT', 30)),
        }

        keywords = os.environ.get(
            'KEYWORDS',
            ';'
        )

        self.data['keywords'] = list(
            filter(None, keywords.split(';'))
        )

        self.data['urls'] = refs.get(region, {})

        if urls:
            all_urls = list(
                range(
                    len(self.data['urls'])
                )
            )
            urls = list(
                map(int, urls.split(','))
            )

            for i in sorted(set(all_urls) - set(urls), reverse=True):
                del self.data['urls'][i]

        self.data['telegram'] = {
            'token': os.environ.get(
                'TELEGRAM_TOKEN',
                ''
            ),
            'chat_passwd': os.environ.get('TELEGRAM_CHAT_PASSWD', '')
        }

        telegram_token = self.data['telegram']['token']

        self.data['telegram'].update({
            'url': f'https://api.telegram.org/bot{telegram_token}/sendMessage'
        })

        self.data['db'] = {
            'client': os.environ.get(
                'MONGO_INITDB_DATABASE',
                'promobot'
            ),
            'host': os.environ.get('DB_HOST', 'localhost:27017'),
            'user': os.environ.get('MONGO_INITDB_ROOT_USERNAME'),
            'passwd': os.environ.get('MONGO_INITDB_ROOT_PASSWORD'),
        }

    def set_proxy(self):
        ip_address = ''
        ips = []
        proxy_file = '/etc/environment'
        url = base64.b64decode(
            os.environ.get('AUTH_PROXY', '')
        ).decode('utf-8').strip()

        proxy_enabled = bool(
            os.environ.get('PROXY_ENABLED', 'false') == 'true'
        )

        if not proxy_enabled:
            if "HTTP_PROXY" in os.environ:
                del os.environ['HTTP_PROXY']

            if "HTTPS_PROXY" in os.environ:
                del os.environ['HTTPS_PROXY']

            return

        if ips:
            ip_address = random.choice(ips)

        elif os.path.exists(proxy_file):
            with open(proxy_file, 'r', encoding='UTF-8') as file:
                get_proxy = re.search(r'http://\S+', file.read())
                file.close()

                ip_address = get_proxy.group()

        ip_auth = ip_address.replace(
            'http://',
            f'http://{url}'
        )

        os.environ['HTTP_PROXY'] = ip_auth
        os.environ['HTTPS_PROXY'] = ip_auth

        self.data['proxies'].update({
            'http': os.environ.get('HTTP_PROXY'),
            'https': os.environ.get('HTTPS_PROXY')
        })
