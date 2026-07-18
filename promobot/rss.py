import feedparser
import re
from bs4 import BeautifulSoup


class Rss:
    def __init__(self, alert):
        self.alert = alert

    @staticmethod
    def clean_text(value):
        return re.sub(r'\n|\t|"', '', str(value)).strip()

    @staticmethod
    def clean_url(value):
        return re.sub(r'\n|\t|"|\(|\)', '', str(value)).strip()

    @staticmethod
    def clean_html(value):
        return BeautifulSoup(
            str(value),
            'html.parser'
        ).get_text(' ', strip=True)

    def fetch(self, src):
        url = src.get('url')
        rss_cfg = src.get('rss', {})

        title_field = rss_cfg.get('title', 'title')
        url_field = rss_cfg.get('url', 'link')
        desc_field = rss_cfg.get('desc', 'summary')

        feed = feedparser.parse(url)
        topic = []

        if feed.bozo:
            self.alert(
                'ERROR',
                f'Malformed RSS/Atom feed {url}: {feed.bozo_exception}'
            )

        for entry in feed.entries:
            raw_desc = entry.get(
                desc_field,
                entry.get('description', '')
            )

            topic.append({
                'title': self.clean_text(entry.get(title_field, '')),
                'desc': self.clean_text(self.clean_html(raw_desc)),
                'url': self.clean_url(entry.get(url_field, ''))
            })

        return topic
