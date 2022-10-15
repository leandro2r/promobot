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
        region = kwargs.get('region')
        urls = kwargs.get('urls')
        options = {
            'br': [
                {
                    'url': 'https://www.hardmob.com.br/forums/407-Promocoes'
                           '?s=&pp=50&daysprune=1&sort=dateline&order=desc',
                    'topic': {
                        'tag': 'div',
                        'attr': {
                            'class': 'threadinfo'
                        }
                    },
                    'thread': {
                        'tag': 'a',
                        'attr': {
                            'class': 'title'
                        }
                    }
                },
                {
                    'url': 'https://www.pelando.com.br/recentes',
                    'tool': 'selenium',
                    'topic': {
                        'tag': 'div',
                        'attr': {
                            'class': 'pf7gf4-0 fhviAs'
                        }
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
                        'attr': {
                            'class': 'pf7gf4-0 fhviAs'
                        }
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
                        'attr': {
                            'class': 'description'
                        }
                    },
                    'thread': {
                        'tag': 'a',
                        'attr': {
                            'data-lightbox-comments': 'data-lightbox-comments'
                        }
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
                        'attr': {
                            'class': 'structItem-title'
                        }
                    },
                    'thread': {
                        'tag': 'a',
                        'attr': {
                            'preview-tooltip': 'data-xf-init'
                        }
                    }
                },
                {
                    'url': 'https://www.ofertaesperta.com',
                    'tool': 'selenium',
                    'topic': {
                        'tag': 'div',
                        'attr': {
                            'class': 'common-card'
                        }
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
                        'attr': {
                            'class': 'e19tro4z0 css-18hidx3 e1ppb8bk0'
                        }
                    },
                    'thread': {
                        'tag': 'a',
                    },
                    'desc': {
                        'tag': 'span',
                        'class': 'ejdy5300 css-1um6tmm e10o2vra0'
                    }
                },
                {
                    'url': 'https://www.promobit.com.br/promocoes/'
                           'melhores-ofertas',
                    'tool': 'selenium',
                    'topic': {
                        'tag': 'div',
                        'attr': {
                            'class': 'e19tro4z0 css-120k3lz e1ppb8bk0'
                        }
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
                    'url': 'https://gafanho.to/facebook',
                    'tool': 'selenium',
                    'topic': {
                        'tag': 'div',
                        'attr': {
                            'ng-init': 'clicked=false'
                        }
                    },
                    'thread': {
                        'tag': 'a',
                    },
                    'desc': {
                        'tag': 'div',
                        'class': 'ng-binding'
                    }
                },
            ],
            'ca': [
                {
                    'url': 'https://forums.redflagdeals.com/hot-deals-f9/',
                    'topic': {
                        'tag': 'div',
                        'attr': {
                            'class': 'thread_info_title'
                        }
                    },
                    'thread': {
                        'tag': 'a',
                        'attr': {
                            'class': 'topic_title_link'
                        }
                    },
                    'desc': {
                        'tag': 'h3',
                        'class': 'topictitle topictitle_has_retailer'
                    }
                },
                {
                    'url': 'https://forums.redflagdeals.com/hot-deals-f9/2/',
                    'topic': {
                        'tag': 'div',
                        'attr': {
                            'class': 'thread_info_title'
                        }
                    },
                    'thread': {
                        'tag': 'a',
                        'attr': {
                            'class': 'topic_title_link'
                        }
                    },
                    'desc': {
                        'tag': 'h3',
                        'class': 'topictitle topictitle_has_retailer'
                    }
                },
                {
                    'url': 'https://forums.redflagdeals.com/'
                           'ongoing-deal-discussion-f129/',
                    'topic': {
                        'tag': 'div',
                        'attr': {
                            'class': 'thread_info_title'
                        }
                    },
                    'thread': {
                        'tag': 'a',
                        'attr': {
                            'class': 'topic_title_link'
                        }
                    },
                    'desc': {
                        'tag': 'h3',
                        'class': 'topictitle topictitle_has_retailer'
                    }
                },
                {
                    'url': 'https://forum.smartcanucks.ca/'
                           'canadian-shopping-deals-flyers/?pp=100',
                    'topic': {
                        'tag': 'h3',
                        'attr': {
                            'class': 'threadtitle'
                        }
                    },
                    'thread': {
                        'tag': 'a',
                        'attr': {
                            'class': 'title'
                        }
                    }
                },
                {
                    'url': 'http://pricefinder.ca/',
                    'topic': {
                        'tag': 'table',
                        'attr': {
                            'class': 'pf-table'
                        }
                    },
                    'thread': {
                        'tag': 'a',
                    },
                    'desc': {
                        'tag': 'td',
                        'class': 'pf-descr pf-shorten'
                    }
                },
                {
                    'url': 'https://www.reddit.com/r/canadadeals/',
                    'tool': 'selenium',
                    'topic': {
                        'tag': 'div',
                        'attr': {
                            'data-click-id': 'background'
                        }
                    },
                    'thread': {
                        'tag': 'a',
                        'attr': {
                            'data-click-id': 'body'
                        }
                    },
                    'desc': {
                        'tag': 'div',
                        'attr': {
                            'data-click-id': 'text'
                        }
                    }
                },
                {
                    'url': 'https://www.reddit.com/r/bapcsalescanada/',
                    'tool': 'selenium',
                    'topic': {
                        'tag': 'div',
                        'attr': {
                            'data-click-id': 'background'
                        }
                    },
                    'thread': {
                        'tag': 'a',
                        'attr': {
                            'data-click-id': 'body'
                        }
                    },
                    'desc': {
                        'tag': 'div',
                        'attr': {
                            'data-click-id': 'text'
                        }
                    }
                },
                {
                    'url': 'https://www.reddit.com/r/ShopCanada/',
                    'tool': 'selenium',
                    'topic': {
                        'tag': 'div',
                        'attr': {
                            'data-click-id': 'background'
                        }
                    },
                    'thread': {
                        'tag': 'a',
                        'attr': {
                            'data-click-id': 'body'
                        }
                    },
                    'desc': {
                        'tag': 'div',
                        'attr': {
                            'data-click-id': 'text'
                        }
                    }
                },
                {
                    'url': 'https://www.cdndeals.ca/',
                    'topic': {
                        'tag': 'div',
                        'attr': {
                            'class': 'fusion-post-content post-content'
                        }
                    },
                    'thread': {
                        'tag': 'a',
                    },
                    'desc': {
                        'tag': 'div',
                        'class': 'fusion-post-content-container'
                    }
                },
            ]
        }

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

        self.data['urls'] = options.get(region, {})

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
