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

        self.db_conn = conn[client]

    def add_config(self, envs):
        data = []
        col = self.db_conn['config']

        if any('delay' or 'reset' or 'timeout' in s for s in envs):
            data = dict(s.split('=') for s in envs)

            col.update_many(
                {},
                {"$set": data},
                upsert=True,
            )

    def list_config(self):
        col = self.db_conn['config']

        configs = list(
            col.find(
                {},
                {'_id': False}
            )
        )

        return configs

    def add_intruder(self, data):
        col = self.db_conn['intruder']

        if not data:
            data = {}

        col.update_one(
            data,
            {'$setOnInsert': data},
            upsert=True,
        )

    def list_users(self, **kwargs):
        users = []
        col = [
            self.db_conn['chat'],
        ]

        if kwargs.get('all', False):
            col.append(self.db_conn['intruder'])

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

    def add_chat(self, data):
        col = self.db_conn['chat']

        if not data:
            data = {}

        col.update_one(
            data,
            {'$setOnInsert': data},
            upsert=True,
        )

    def del_chat(self, data):
        col = self.db_conn['chat']

        if data:
            col.delete_many({
                'id': data.get('id')
            })
            return True

        return False

    def find_chat(self, chat_id):
        col = self.db_conn['chat']

        chat = col.count_documents({
            'id': chat_id
        })

        return chat

    def list_chats(self):
        col = self.db_conn['chat']

        chat_ids = list(
            col.distinct(
                'id'
            )
        )

        return chat_ids

    def add_keywords(self, keywords, **kwargs):
        data = {}
        col = self.db_conn['keyword']

        if not keywords:
            keywords = []

        if kwargs.get('initial'):
            initial = os.environ.get(
                'INITIAL_KEYWORDS'
            )
            keywords = list(
                filter(None, initial.split(';'))
            )

        if keywords:
            for k in keywords:
                data['keyword'] = k

                col.update_one(
                    data,
                    {"$set": data},
                    upsert=True,
                )

    def del_keywords(self, keywords):
        col = self.db_conn['keyword']
        lis = col.distinct('keyword')

        for i in keywords:
            index = int(i) - 1

            col.remove({
                'keyword': lis[index]
            })

        if keywords:
            return True

        return False

    def list_keywords(self):
        col = self.db_conn['keyword']

        keywords = list(
            col.distinct('keyword')
        )

        return keywords
