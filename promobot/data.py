import os
import pymongo


class Data():
    def __init__(self, config):
        client = config.get('client')

        conn = pymongo.MongoClient(
            host=config.get('host'),
            username=config.get('user'),
            password=config.get('passwd'),
            appname='promobot',
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

    def list_user(self, **kwargs):
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

    def list_chat(self, **kwargs):
        col = self.db_conn['chat']
        default = kwargs.get('default', [])

        try:
            chat_ids = list(
                col.distinct(
                    'id'
                )
            )
        except pymongo.errors.ServerSelectionTimeoutError:
            chat_ids = []

        if not chat_ids and default:
            chat_ids = default

        return chat_ids

    def add_keyword(self, keywords, **kwargs):
        data = {}
        col = self.db_conn['keyword']

        if not keywords:
            keywords = []

        if kwargs.get('initial'):
            initial = os.environ.get(
                'INITIAL_KEYWORDS',
                ';'
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

    def del_keyword(self, indexes):
        col = self.db_conn['keyword']
        lis = col.distinct('keyword')
        keywords = []

        for i in indexes:
            index = int(i) - 1

            keywords.append(
                lis[index]
            )

        if self.del_result(keywords):
            col.delete_many({
                'keyword': {'$in': keywords}
            })

        if keywords:
            return True

        return False

    def list_keyword(self):
        col = self.db_conn['keyword']

        keywords = list(
            col.distinct('keyword')
        )

        return keywords

    def add_result(self, data):
        col = self.db_conn['result']

        if data:
            last_data = {}
            last_id = {}
            updated_data = {}

            last_one = col.find_one({}, sort=[('_id', -1)])

            if last_one:
                last_data = last_one.get('data')
                last_id = {
                    '_id': last_one.get('_id')
                }

            for key in (last_data | data).keys():
                data_merged = last_data.get(key, []) + data.get(key, [])
                updated_data[key] = list(
                    {
                        i['url']: i for i in data_merged
                    }.values()
                )

            col.update_one(
                last_id,
                {'$set': {'data': updated_data}},
                upsert=True
            )

    def del_result(self, keywords):
        col = self.db_conn['result']

        for i in keywords:
            col.update_many(
                {},
                {'$unset': {f'data.{i}': ''}},
                upsert=True
            )

        if keywords:
            return True

        return False

    def list_result(self):
        col = self.db_conn['result']

        try:
            result = col.find_one(
                {},
                {'_id': False}
            )
        except pymongo.errors.ServerSelectionTimeoutError:
            result = {}

        if result:
            result = result.get('data')
        else:
            result = {}

        return result
