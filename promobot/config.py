import base64
import os
import random
import re


class Config():
    data = {
        'proxies': {
            'http': '',
            'https': ''
        }
    }

    def __init__(self, **kwargs):
        urls = kwargs.get('urls')
        self.set_proxy()

        self.data['monitor'] = {
            'delay': int(os.environ.get('DELAY', 40)),
            'muted': bool(os.environ.get('MUTED', 'false') == 'true'),
            'reset': int(os.environ.get('RESET_TIME', 72)),
            'timeout': int(os.environ.get('TIMEOUT', 30)),
        }

        self.data['urls'] = [
            {
                'url': 'https://www.hardmob.com.br/forums/407-Promocoes'
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
                'tool': 'selenium',
                'topic': {
                    'tag': 'div',
                    'class': 'pf7gf4-0 fhviAs'
                },
                'thread': {
                    'tag': 'a',
                },
                'desc': {
                    'tag': 'a',
                    'class': 'pf7gf4-4 eUBBJN'
                }
            },
            {
                'url': 'https://www.pelando.com.br',
                'tool': 'selenium',
                'topic': {
                    'tag': 'div',
                    'class': 'pf7gf4-0 fhviAs'
                },
                'thread': {
                    'tag': 'a',
                },
                'desc': {
                    'tag': 'a',
                    'class': 'pf7gf4-4 eUBBJN'
                }
            },
            {
                'url': 'https://www.gatry.com',
                'topic': {
                    'tag': 'div',
                    'class': 'description'
                },
                'thread': {
                    'tag': 'a',
                },
                'desc': {
                    'tag': 'p',
                    'class': 'comment text-break'
                }
            },
            {
                'url': 'https://forum.adrenaline.com.br/'
                       'forums/for-sale.221',
                'topic': {
                    'tag': 'div',
                    'class': 'structItem-title'
                },
                'thread': {
                    'tag': 'a',
                    'preview-tooltip': 'data-xf-init'
                }
            },
            {
                'url': 'https://www.ofertaesperta.com',
                'tool': 'selenium',
                'topic': {
                    'tag': 'div',
                    'class': 'common-card'
                },
                'thread': {
                    'tag': 'a',
                },
                'desc': {
                    'tag': 'div',
                    'class': 'store-icon'
                }
            },
            {
                'url': 'https://www.promobit.com.br',
                'tool': 'selenium',
                'topic': {
                    'tag': 'div',
                    'class': 'e19tro4z0 css-120k3lz e1ppb8bk0'
                },
                'thread': {
                    'tag': 'a',
                },
                'desc': {
                    'tag': 'span',
                    'class': 'ejdy5300 css-9zk395 e10o2vra0'
                }
            },
            {
                'url': 'https://www.promobit.com.br/promocoes/'
                       'melhores-ofertas',
                'tool': 'selenium',
                'topic': {
                    'tag': 'div',
                    'class': 'e19tro4z0 css-120k3lz e1ppb8bk0'
                },
                'thread': {
                    'tag': 'a',
                },
                'desc': {
                    'tag': 'span',
                    'class': 'ejdy5300 css-9zk395 e10o2vra0'
                }
            },
        ]

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
            'host': os.environ.get('DB_HOST', 'localhost:27017'),
            'user': os.environ.get('MONGO_INITDB_ROOT_USERNAME'),
            'passwd': os.environ.get('MONGO_INITDB_ROOT_PASSWORD'),
            'client': os.environ.get(
                'MONGO_INITDB_DATABASE',
                'promobot'
            ),
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
