import logging
import re
import time
from datetime import datetime
import telebot
from kubernetes import client, config as conf

if __package__ is None or __package__ == '':
    from config import Config
    from data import Data
else:
    from promobot.config import Config
    from promobot.data import Data


logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

config = Config().data
bot = telebot.TeleBot(
    config['telegram'].get('token')
)

database = Data(
    config.get('db')
)


def handle_help(message, **kwargs):
    msg = ''
    support = kwargs.get('support')

    if message.chat.type == 'private':
        if database.find_chat(message.chat.id):
            msg = (
                'You can chat with me using one of the '
                'following commands below:\n/{}'.format(
                    '\n/'.join(support)
                )
            )

    return msg


def handle_intro(message, **kwargs):
    msg = ''
    cmd = kwargs.get('cmd')
    args = message.text.split()[1:]

    if message.chat.type == 'private':
        username = ''
        if message.chat.username:
            username = f'@{message.chat.username}'

        data = {
            'id': message.chat.id,
            'user': (
                f'{message.chat.first_name} {message.chat.last_name} '
                f'({username})'
            ),
            'username': username,
        }

        if len(args) > 0:
            if config['telegram'].get('chat_passwd') == args[0]:
                if 'start' in cmd:
                    msg = 'Now you gonna receive all reports!'
                    database.add_chat(data)
                elif 'stop' in cmd:
                    msg = 'You will no longer receive the reports!'
                    database.del_chat(data)
                else:
                    forall = 'I\'m under maintenance...'
                    msg = 'Message has been sent for all chats!'

                    if len(args) > 1:
                        forall = ' '.join(args[1:])

                    for chat_id in database.list_chats():
                        bot.send_message(
                            chat_id,
                            text=f'Hey all, {forall}'
                        )
            else:
                data.update({
                    'date': datetime.utcfromtimestamp(
                        message.date
                    ).strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                })
                database.add_intruder(data)

    return msg


def handle_mgmt(message, **kwargs):
    msg = ''
    res = ''
    cmd = kwargs.get('cmd')
    args = message.text.split()[1:]

    if message.chat.type == 'private':
        if database.find_chat(message.chat.id):
            if 'kube' in cmd:
                info = 'status'
                if len(args) > 0:
                    info = args[0]

                msg = manage_kube(info)
            elif 'config' in cmd:
                if len(args) > 0:
                    database.add_config(args)

                for data in database.list_config():
                    for k, val in data.items():
                        res += f'{k}={val}\n'

                if 'delay' not in res:
                    res += 'delay=<default>\n'
                if 'reset' not in res:
                    res += 'reset=<default>\n'
                if 'timeout' not in res:
                    res += 'timeout=<default>\n'

                msg = f'Configs:\n```\n{res}```'
            elif 'who' in cmd:
                res = '\n'.join(
                    str(i) for i in database.list_users(all=True)
                )

                msg = f'Users:\n{res}'
            elif 'url' in cmd:
                for k in config.get('urls'):
                    res += '{}\n'.format(
                        k.get('url')
                    )

                msg = f'URLs:\n```\n{res}```'
            else:
                msg = 'Empty keyword list.'

                if len(args) > 0:
                    if 'add' in cmd:
                        database.add_keywords(args)
                    elif 'del' in cmd:
                        database.del_keywords(args)

                items = database.list_keywords()

                if items:
                    for i in range(len(items)):
                        items[i] = '{:02d}) {}'.format(
                            i + 1,
                            items[i],
                        )

                    msg = '```\n{}```'.format(
                        '\n'.join(items),
                    )

    return msg


def manage_kube(info):
    msg = ''
    name = 'promobot'

    try:
        conf.load_incluster_config()
    except conf.config_exception.ConfigException:
        conf.load_kube_config()

    if info == 'reload':
        v1_api = client.AppsV1Api()

        for i in range(2):
            v1_api.patch_namespaced_deployment_scale(
                name=name,
                namespace=name,
                body={"spec": {"replicas": i}},
            )

            msg += 'Scaling replica to {i}...\n'

        msg = f'```\n{msg}```'

    else:
        try:
            tail_lines = int(info)
        except ValueError:
            tail_lines = 3

        v1_api = client.CoreV1Api()

        pod = v1_api.list_namespaced_pod(
            watch=False,
            namespace=name,
        )

        for i in pod.items:
            for status in i.status.container_statuses:
                state = 'Running'
                if not status.state.running:
                    state = 'Not running'

                started_at = datetime.strptime(
                    str(status.state.running.started_at),
                    '%Y-%m-%d %H:%M:%S+00:00'
                )

                runtime = datetime.utcnow() - started_at

                log = v1_api.read_namespaced_pod_log(
                    name=i.metadata.name,
                    namespace=i.metadata.namespace,
                    container=status.name,
                    tail_lines=tail_lines,
                )

                msg += '{} {} - {} restarts ({})\n```\n{}```\n\n'.format(
                    state,
                    runtime,
                    status.restart_count,
                    status.name.title(),
                    log,
                )

    return msg


@bot.message_handler(func=lambda message: True)
def bot_reply(message):
    cmd = message.text.split()[0]

    if cmd:
        cmd = re.sub('[^a-z]+', '', cmd.lower())

    data = {
        'mgmt': [
            'add', 'del', 'list', 'who', 'kube', 'config', 'url'
        ],
        'help': [
            'help'
        ],
        'intro': [
            'start', 'stop', 'forall'
        ],
    }

    for opt in data:
        if cmd in data.get(opt):
            if opt == 'mgmt':
                res = handle_mgmt(
                    message,
                    cmd=cmd,
                )
            elif opt == 'help':
                res = handle_help(
                    message,
                    support=data.get('mgmt'),
                )
            elif opt == 'intro':
                res = handle_intro(
                    message,
                    cmd=cmd,
                )

            if not res:
                res = 'This message costed me R$0,31.'

            try:
                bot.reply_to(
                    message,
                    res,
                    parse_mode='Markdown',
                )
            except Exception:
                pass


def main():
    try:
        bot.polling(none_stop=True)
    except Exception:
        time.sleep(20)
