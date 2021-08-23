import base64
import os
import random
import re
from datetime import datetime


class Config():
    data = {
        'proxies': {
            'http': '',
            'https': ''
        }
    }

    def __init__(self):
        self.set_proxy()

        self.data['monitor'] = {
            'delay': int(os.environ.get('DELAY', 10)),
            'muted': eval(os.environ.get('MUTED', 'false').title()),
            'reset': int(os.environ.get('RESET_TIME', 24)),
            'timeout': int(os.environ.get('TIMEOUT', 10)),
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
                'topic': {
                    'tag': 'div',
                    'class': 'sc-1t2mqdt-9 jmQjPk'
                },
                'thread': {
                    'tag': 'a',
                },
                'desc': {
                    'tag': 'a',
                    'class': 'sc-1t2mqdt-10 oueGS'
                }
            },
            {
                'url': 'https://www.pelando.com.br/quente',
                'topic': {
                    'tag': 'div',
                    'class': 'sc-1t2mqdt-9 jmQjPk'
                },
                'thread': {
                    'tag': 'a',
                },
                'desc': {
                    'tag': 'a',
                    'class': 'sc-1t2mqdt-10 oueGS'
                }
            },
            {
                'url': 'https://www.gatry.com',
                'topic': {
                    'tag': 'div',
                    'class': 'informacoes'
                },
                'thread': {
                    'tag': 'a',
                    'class': 'mais hidden-xs'
                },
                'desc': {
                    'tag': 'p',
                    'class': 'preco comentario clear'
                }
            },
            # {
            #     'url': 'https://forum.adrenaline.com.br/'
            #            'forums/for-sale.221',
            #     'topic': {
            #         'tag': 'div',
            #         'class': 'structItem-title'
            #     },
            #     'thread': {
            #         'tag': 'a',
            #         'preview-tooltip': 'data-xf-init'
            #     }
            # },
            {
                'url': 'https://www.ofertaesperta.com?page=1',
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
                'url': 'https://www.ofertaesperta.com?page=2',
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
                'topic': {
                    'tag': 'div',
                    'class': 'pr-tl-card'
                },
                'thread': {
                    'tag': 'a',
                    'class': 'access_url'
                },
                'desc': {
                    'tag': 'div',
                    'class': 'where'
                }
            },
            {
                'url': 'https://www.promobit.com.br/promocoes/'
                       'melhores-ofertas',
                'topic': {
                    'tag': 'div',
                    'class': 'pr-tl-card'
                },
                'thread': {
                    'tag': 'a',
                    'class': 'access_url'
                },
                'desc': {
                    'tag': 'div',
                    'class': 'where'
                }
            },
        ]

        self.data['telegram'] = {
            'token': os.environ.get(
                'TELEGRAM_TOKEN',
                ''
            ),
            'chat_passwd': os.environ.get('TELEGRAM_CHAT_PASSWD', '')
        }

        self.data['telegram'].update({
            'url': 'https://api.telegram.org/bot{}/sendMessage'.format(
                self.data['telegram']['token']
            )
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
