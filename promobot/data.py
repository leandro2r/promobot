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

    def add_keywords(self, keywords=[]):
        d = []
        col = self.db['keyword']

        if not keywords:
            initial = os.environ.get(
                'INITIAL_KEYWORDS'
            )
            keywords = initial.split(';')

        for v in keywords:
            d.append({
                'keyword': v,
            })

        col.insert_many(
            d,
            ordered=False,
        )

    def get_keywords(self):
        col = self.db['keyword']

        keywords = list(
            col.distinct(
                'keyword'
            )
        )

        return keywords

    def del_keywords(self, keywords):
        col = self.db['keyword']

        if keywords:
            col.delete_many({
                'keyword': {
                    '$in': keywords
                }
            })

            return True

        return False
