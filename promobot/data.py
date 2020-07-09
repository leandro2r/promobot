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

    def add_intruder(self, d={}):
        col = self.db['intruder']

        col.update_one(
            d,
            {'$setOnInsert': d},
            upsert=True,
        )

    def list_users(self, **kwargs):
        users = []
        col = [
            self.db['chat'],
        ]

        if kwargs.get('all', False):
            col.append(self.db['intruder'])

        for i in range(len(col)):
            users.extend(
                list(
                    col[i].distinct(
                        'user'
                    )
                )
            )

            if i < len(col) - 1:
                users.append('---')

        return users

    def add_chat(self, d={}):
        col = self.db['chat']

        col.update_one(
            d,
            {'$setOnInsert': d},
            upsert=True,
        )

    def del_chat(self, d):
        col = self.db['chat']

        if d:
            col.delete_many({
                'id':  d.get('id')
            })
            return True

        return False

    def find_chat(self, id):
        col = self.db['chat']

        chat = col.count_documents({
            'id': id
        })

        return chat

    def list_chats(self):
        col = self.db['chat']

        chat_ids = list(
            col.distinct(
                'id'
            )
        )

        return chat_ids

    def add_keywords(self, keywords=[], **kwargs):
        d = []
        col = self.db['keyword']

        if kwargs.get('initial'):
            initial = os.environ.get(
                'INITIAL_KEYWORDS'
            )
            keywords = list(
                filter(None, initial.split(';'))
            )

        if keywords:
            for v in keywords:
                d.append({
                    'keyword': v,
                })

            col.insert_many(
                d,
                ordered=False,
            )

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

    def list_keywords(self):
        col = self.db['keyword']

        keywords = list(
            col.distinct(
                'keyword'
            )
        )

        return keywords
