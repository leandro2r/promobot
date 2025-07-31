import os
import yaml

from swiftshadow.classes import ProxyInterface


class Config():
    data = {}

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

        self.set_proxy(region)

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

    def set_proxy(self, region):
        countries = []
        proxy_http = ''
        proxy_https = ''

        countries.append(region.upper())

        try:
            proxy_http = ProxyInterface(
                countries=countries,
                protocol="http"
            ).get().as_string()
    
            proxy_https = ProxyInterface(
                countries=countries,
                protocol="https"
            ).get().as_string()

            print(
                (
                    f'Setting {region} proxies '
                    f'HTTP {proxy_http} and HTTPS {proxy_https}'
                )
            )
        except Exception as error:
            print(
                (
                    f'Error when retrieving {region} '
                    f'HTTP and HTTPS proxies: {error}'
                )
            )

        self.data['proxies'] = {
            'http': proxy_http,
            'https': proxy_https
        }
