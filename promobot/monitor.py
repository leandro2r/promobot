import os
import re
import threading
import time
import urllib.request
from datetime import datetime, timedelta
from http.client import IncompleteRead
from json import dumps
from bs4 import BeautifulSoup
from pymongo.errors import ServerSelectionTimeoutError, AutoReconnect
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from urllib3.exceptions import MaxRetryError


def mount(src, each, t_title):
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

    desc = re.sub(r'\n|\t|"', '', str(desc))
    title = re.sub(r'\n|\t|"', '', str(title))
    url = re.sub(
        r'\n|\t|"|\(|\)',
        '',
        str(url)
    )

    return {
        'title': title,
        'desc': desc,
        'url': url,
    }


class Monitor():
    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/35.0.1916.47 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,'
                  'application/xml;q=0.9,*/*;q=0.8'
    }
    options = Options()

    def __init__(self, **kwargs):
        self.alert = kwargs.get('alert')
        self.config = kwargs.get('config')
        self.db_data = kwargs.get('data')
        self.report = kwargs.get('report')

        self.data = self.db_data.list_result()

        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--headless')
        self.options.add_experimental_option('useAutomationExtension', False)

        self.options.add_argument('--proxy-bypass-list=*')
        self.options.add_argument('--proxy-server="direct://"')
        self.options.add_argument('--safe-mode')
        self.options.add_argument('--log-level=3')
        self.options.add_argument('--output=/dev/null')
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument(
            '--js-flags="--max_old_space_size=256 --max_semi_space_size=256"'
        )
        self.options.add_argument('blink-settings=imagesEnabled=false')

        self.options.add_argument('--disable-crash-reporter')
        self.options.add_argument('--disable-default-apps')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-extensions')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--disable-impl-side-painting')
        self.options.add_argument('--disable-in-process-stack-traces')
        self.options.add_argument('--disable-infobars')
        self.options.add_argument('--disable-logging')
        self.options.add_argument('--disable-popup-blocking')
        self.options.add_argument('--disable-setuid-sandbox')

        self.options.add_experimental_option(
            'prefs',
            {'profile.managed_default_content_settings.images': 2}
        )

    def manage_config(self, configs):
        for i in configs:
            if i.get('delay'):
                self.config['monitor'].update({
                    'delay': int(i.get('delay'))
                })

            if i.get('reset'):
                self.config['monitor'].update({
                    'reset': int(i.get('reset'))
                })

            if i.get('timeout'):
                self.config['monitor'].update({
                    'timeout': int(i.get('timeout'))
                })

    def manage_keyword(self, keys):
        result = []
        add = list(
            set(keys) - set(self.data.keys())
        )
        remove = list(
            set(self.data.keys()) - set(keys)
        )

        for k in add:
            self.data.update({
                k: []
            })

        for k in remove:
            self.data.pop(k)

        if add:
            action = 'Adding'
            result = add
        elif remove:
            action = 'Removing'
            result = remove

        if result:
            self.alert(
                'INFO',
                f'{action} keywords: {result}'
            )

    def lookup(self, keyword, data, add):
        src = [
            data.get('url', '').replace('-', ' '),
            data.get('desc'),
        ]

        for text in src:
            if re.match(
                    r'.*{}.*'.format(keyword),
                    str(text),
                    re.IGNORECASE,
            ):
                for val in self.data.get(keyword):
                    if val.get('url') in data.get('url'):
                        add = False
                        break

                if add:
                    data.update({
                        'url': re.sub(
                            r'(\?)(?!.*\1).*$',
                            '',
                            data.get('url')
                        ),
                        'datetime': datetime.now().strftime(
                            '%d-%m-%Y %H:%M'
                        )
                    })

                    self.data[keyword].append(
                        data
                    )

                    self.report(
                        'Keyword: **[{}]({})**'.format(
                            keyword,
                            data.get('url'),
                        )
                    )

                break

    def get_promo(self, src):
        content = ''
        delay = self.config['monitor'].get('delay') * 2
        timeout = self.config['monitor'].get('timeout')
        topic = []

        while len(topic) == 0:
            try:
                if src.get('tool', '').lower() == 'selenium':
                    driver = webdriver.Chrome(
                        options=self.options,
                        service_log_path=os.path.devnull,
                    )

                    driver.set_script_timeout(timeout)
                    driver.set_page_load_timeout(-1)

                    driver.get(
                        src.get('url')
                    )

                    height = driver.execute_script(
                        'return document.body.scrollHeight'
                    )

                    if height:
                        limit = height * 1.5
                        wait_time = 0

                        while height <= limit:
                            driver.execute_script(
                                'window.scrollTo(0, '
                                'document.body.scrollHeight);'
                            )

                            wait_time += 1
                            time.sleep(wait_time)

                            height = driver.execute_script(
                                'return document.body.scrollHeight'
                            )

                            if wait_time > 5:
                                break

                    content = driver.page_source
                else:
                    req = urllib.request.Request(
                        url=src.get('url'),
                        headers=self.header
                    )

                    content = urllib.request.urlopen(
                        req,
                        timeout=timeout,
                    ).read()

                if content:
                    soup = BeautifulSoup(
                        content,
                        'html.parser',
                    )

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
                            'Error on searching topics in {}: {:50.50}'.format(
                                src.get('url'),
                                str(soup)
                            )
                        )

            except (
                urllib.error.HTTPError,
                WebDriverException,
                MaxRetryError,
                ConnectionError,
                IncompleteRead,
                OSError
            ) as error:
                self.alert(
                    'ERROR',
                    'Error on getting data from {}: {}'.format(
                        src.get('url'),
                        error,
                    )
                )

            if src.get('tool', '').lower() == 'selenium':
                try:
                    driver.quit()
                except UnboundLocalError as error:
                    self.alert(
                        'WARNING',
                        'Failed to quit selenium driver from {}: {}'.format(
                            src.get('url'),
                            error,
                        )
                    )

            if len(topic) == 0:
                time.sleep(delay)

        return topic

    def monitor(self, src):
        promo = self.get_promo(src)

        for key in list(self.data):
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
                    data = mount(
                        src,
                        each,
                        t_title
                    )

                    self.lookup(
                        key,
                        data,
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

    def clean_up(self, hours):
        self.alert(
            'INFO',
            'Checking old values to be cleaned up'
        )

        for k, val in self.data.items():
            for i in range(len(val)):
                if i < len(val):
                    cur = time.mktime(
                        datetime.strptime(
                            val[i]['datetime'], '%d-%m-%Y %H:%M'
                        ).timetuple()
                    )
                    old = time.mktime(
                        (datetime.now() - timedelta(hours=hours)).timetuple()
                    )

                    if cur <= old:
                        self.alert(
                            'INFO',
                            (
                                'Clean up {}º {} '
                                'value from {}'
                            ).format(
                                i + 1,
                                k,
                                val[i]['datetime'],
                            )
                        )
                        del val[i]

    def runner(self, url):
        runtime = 0

        self.alert(
            'INFO',
            'Starting runner at {}'.format(
                url.get('url'),
            )
        )

        while True:
            try:
                config = self.db_data.list_config()
                keywords = self.db_data.list_keyword()

                self.manage_config(
                    config
                )
                self.manage_keyword(
                    keywords
                )

                self.db_data.add_result(
                    self.data
                )

                self.monitor(url)
            except (ServerSelectionTimeoutError, AutoReconnect) as error:
                self.alert(
                    'ERROR',
                    f'Error on listing data from database: {error}'
                )

            delay = self.config['monitor']['delay']
            reset = self.config['monitor']['reset']

            time.sleep(delay)
            runtime += delay

            if runtime >= 14400:
                self.clean_up(reset)
                runtime = 0

    def main(self):
        proc = []
        urls = []

        sites = self.config.get('urls', [])
        dft = [x for x in sites if not x.get('tool')]
        sel = [x for x in sites if x.get('tool')]

        for i in range(max(len(dft), len(sel))):
            if len(dft) > i:
                urls.append(dft[i])
            if len(sel) > i:
                urls.append(sel[i])

        self.report(
            'Promobot has been started!'
        )

        num_urls = len(urls)

        for i in range(num_urls):
            module = threading.Thread(
                target=self.runner,
                args=(
                    urls[i],
                )
            )
            proc.append(module)

        for i in proc:
            i.start()
            time.sleep(
                self.config['monitor'].get('delay', 60) / num_urls
            )

        for i in proc:
            i.join()
