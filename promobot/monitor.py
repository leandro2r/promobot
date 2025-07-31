import os
import re
import threading
import time
import requests
from datetime import datetime
from http.client import IncompleteRead
from json import dumps
from random import randint
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from pymongo.errors import ServerSelectionTimeoutError, AutoReconnect
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException


def mount(src, each, t_title):
    desc = each.get('title', '')
    title = t_title.find(text=True)
    url = t_title.get('href', '')

    if src.get('desc'):
        desc = each.find(
            src['desc'].get('tag'),
            src['desc'].get('attr', {})
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

        url = f'{domain}/{re.sub(r"^/", "", url)}'

    desc = re.sub(r'\n|\t|"', '', str(desc))
    title = re.sub(r'\n|\t|"', '', str(title))
    url = re.sub(
        r'\n|\t|"|\(|\)',
        '',
        str(url)
    )

    return {
        'title': title.strip(),
        'desc': desc.strip(),
        'url': url.strip(),
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
        self.flag_result = False

        self.chat_ids = self.db_data.list_chat()
        self.data = self.db_data.clean_up_result(
            self.config['monitor']['reset']
        )

        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--headless')
        self.options.add_argument("start-maximized")
        self.options.add_experimental_option(
            "excludeSwitches", 
            ["enable-automation"]
        )
        self.options.add_experimental_option(
            'useAutomationExtension', 
            False
        )

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
            data.get('title'),
            data.get('desc'),
        ]

        for text in src:
            if re.match(
                    rf'.*{keyword}.*',
                    str(text),
                    re.IGNORECASE,
            ):
                for val in self.data.get(keyword):
                    if val.get('url') in data.get('url'):
                        add = False
                        break

                if add:
                    self.flag_result = True

                    data.update({
                        'datetime': datetime.now().strftime(
                            '%d-%m-%Y %H:%M'
                        )
                    })

                    self.data[keyword].append(
                        data
                    )

                    self.report(
                        f'Keyword: **[{keyword}]({data.get("url")})**',
                        chat_ids=self.chat_ids
                    )

                break

    def load_page(self, driver, url):
        try:
            driver.refresh()
        except WebDriverException as error:
            self.alert(
                'ERROR',
                f'Error on refreshing page {url}: {error}'
            )
            driver.close()
            driver = self.init_driver(driver, url)

        height = driver.execute_script(
            'return document.documentElement.scrollHeight'
        )

        if height:
            limit = height * 1.5
            wait_time = 0

            while height <= limit:
                driver.execute_script(
                    'window.scrollTo(0, '
                    'document.documentElement.scrollHeight);'
                )

                wait_time += 1
                time.sleep(wait_time)

                height = driver.execute_script(
                    'return document.documentElement.scrollHeight'
                )

                if wait_time > 5:
                    break

        return driver.page_source

    def get_topic(self, src, driver):
        content = ''
        delay = self.config['monitor'].get('delay') * 2
        topic = []

        while len(topic) == 0:
            try:
                if driver:
                    content = self.load_page(
                        driver,
                        src.get('url')
                    )
                else:
                    content = requests.get(
                        src.get('url'),
                        headers=self.header
                    ).text

                if content:
                    soup = BeautifulSoup(
                        content,
                        'html.parser',
                    )

                    topic = soup.findAll(
                        src['topic']['tag'],
                        src['topic'].get('attr', {})
                    )

                    if len(topic) == 0:
                        self.alert(
                            'ERROR',
                            (
                                'Error on searching topics in '
                                f'{src.get("url")}: {str(soup):50.50}'
                            )
                        )

            except (
                requests.exceptions.HTTPError,
                requests.exceptions.ConnectionError,
                ConnectionError,
                IncompleteRead,
                OSError,
                TimeoutException
            ) as error:
                self.alert(
                    'ERROR',
                    f'Error on getting data from {src.get("url")}: {error}'
                )

            if len(topic) == 0:
                time.sleep(delay)

        return topic

    def start_lookup(self, src, topics, key):
        add = True

        for promo in topics:
            t_title = promo.find(
                src['thread']['tag'],
                src['thread'].get('attr', {})
            )

            if t_title:
                data = mount(
                    src,
                    promo,
                    t_title
                )

                self.lookup(
                    key,
                    data,
                    add,
                )

    def monitor(self, src, driver):
        keys = list(self.data)
        topics = self.get_topic(src, driver)

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(self.start_lookup, src, topics, key): key
                for key in keys
            }

            for future in as_completed(futures):
                key = futures[future]
                try:
                    future.result()
                except Exception as error:
                    self.alert('ERROR', f'Error processing key {key}: {error}')

        self.alert(
            'DEBUG',
            f'\n{dumps(self.data, indent=2, ensure_ascii=False)}'
        )

        self.alert(
            'INFO',
            f'Last lookup from {src.get("url")}'
        )

    def init_driver(self, driver, url):
        timeout = self.config['monitor'].get('timeout')

        if not driver:
            driver = webdriver.Chrome(
                options=self.options,
                service_log_path=os.path.devnull,
            )

            driver.set_script_timeout(timeout)
            driver.set_page_load_timeout(-1)

            stealth(
                driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                run_on_insecure_origins=False,
            )

        try:
            driver.get(url)
        except WebDriverException as error:
            driver.delete_all_cookies()
            self.alert(
                'ERROR',
                f'Error on loading {url}: {error}'
            )

        return driver

    def runner(self, url):
        delay = 0
        driver = {}
        runtime = randint(0, 300)

        self.alert(
            'INFO',
            f'Starting runner at {url.get("url")}'
        )

        if url.get('tool', '').lower() == 'selenium':
            driver = self.init_driver(
                driver,
                url.get('url')
            )

        while time.sleep(delay) is None:
            try:
                config = self.db_data.list_config()
                keywords = self.db_data.list_keyword()

                self.manage_config(
                    config
                )
                self.manage_keyword(
                    keywords
                )

                self.monitor(url, driver)

                if self.flag_result:
                    self.db_data.add_result(
                        self.data
                    )
                    self.flag_result = False
            except (ServerSelectionTimeoutError, AutoReconnect) as error:
                self.alert(
                    'ERROR',
                    f'Error on listing data from database: {error}'
                )

            delay = self.config['monitor']['delay']
            runtime += delay

            if runtime >= 14700:
                reset = self.config['monitor']['reset']
                runtime = randint(0, 300)

                self.alert(
                    'INFO',
                    f'Checking any data older than {reset} hours...'
                )

                reset = self.config['monitor']['reset']
                self.data = self.db_data.clean_up_result(reset)

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
            'Promobot has been started!',
            chat_ids=self.chat_ids
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
