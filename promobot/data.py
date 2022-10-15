import time
from datetime import datetime, timedelta
import pymongo


class Data():
    def __init__(self, config):
        client = config['db'].get('client')

        conn = pymongo.MongoClient(
            host=config['db'].get('host'),
            username=config['db'].get('user'),
            password=config['db'].get('passwd'),
            appname='promobot',
        )

        self.db_conn = conn[client]

        if config.get('keywords'):
            self.add_keyword(
                config.get('keywords')
            )

        if config.get('urls'):
            self.add_url(
                config.get('urls')
            )

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

    def add_keyword(self, keywords):
        data = {}
        col = self.db_conn['keyword']

        if not keywords:
            keywords = []

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
            res_data = {}
            res_id = {}
            updated_data = {}

            res = self.list_result()

            if res:
                res_data = res.get('data')
                res_id = {
                    '_id': res.get('_id')
                }

            for key in (res_data | data).keys():
                data_merged = res_data.get(key, []) + data.get(key, [])
                updated_data[key] = list(
                    {
                        i['url']: i for i in data_merged
                    }.values()
                )

            col.update_one(
                res_id,
                {'$set': {'data': updated_data}},
                upsert=True
            )

    def clean_up_result(self, hours):
        col = self.db_conn['result']

        cleaned_up = False

        res = self.list_result()
        res_data = res.get('data', {})
        res_id = {
            '_id': res.get('_id')
        }

        for val in res_data.values():
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
                        cleaned_up = True
                        del val[i]

        if cleaned_up:
            col.update_one(
                res_id,
                {'$set': {'data': res_data}},
                upsert=True
            )

        return res_data

    def del_result(self, keywords):
        col = self.db_conn['result']

        res = self.list_result()

        if res:
            res_data = res.get('data', {})
            res_id = {
                '_id': res.get('_id')
            }

            for i in keywords:
                res_data.pop(i)

            col.update_one(
                res_id,
                {'$set': {'data': res_data}},
                upsert=True
            )

            if keywords:
                return True

        return False

    def list_result(self, **kwargs):
        col = self.db_conn['result']
        get_id = kwargs.get('id', True)

        try:
            data = col.find_one(
                {},
                sort=[('_id', -1)]
            )
        except pymongo.errors.ServerSelectionTimeoutError:
            data = {}

        if data:
            result = {
                '_id': data.get('_id'),
                'data': data.get('data')
            }
            if not get_id:
                result = result.get('data')
        else:
            result = {}

        return result

    def add_url(self, urls):
        data = {}
        col = self.db_conn['url']

        col.delete_many({})

        if not urls:
            urls = []

        if urls:
            data['url'] = []

            for k in urls:
                data['url'].append(
                    k.get('url')
                )

            col.insert_one(
                data
            )

    def list_url(self):
        col = self.db_conn['url']

        urls = col.find_one(
            {},
            {'_id': False}
        ).get('url')

        return urls
