import os
import pymongo


class Data():
    def __init__(self, config):
        client = config.get('client')

        conn = pymongo.MongoClient(
            host=config.get('host'),
            username=config.get('user'),
            password=config.get('passwd'),
        )

        self.db = conn[client]

    def set_inital_keywords(self):
        d = []
        initial = os.environ.get('INITIAL_KEYWORDS')

        if initial:
            for v in initial.split(';') :
                d.append({
                    'keyword': v,
                })

            col = self.db['keyword']
            col.insert_many(
                d,
                ordered=False
            )

    def get_keywords(self):
        col = self.db['keyword']

        keywords = list(
            col.distinct(
                'keyword'
            )
        )

        return keywords
