import logging
import re
import time
from datetime import datetime
import telebot
from kubernetes import client, config as conf

if __package__ is None or __package__ == '':
    from config import Config
    from data import Data
    from log import Log
else:
    from promobot.config import Config
    from promobot.data import Data
    from promobot.log import Log


logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

config = Config().data
bot = telebot.TeleBot(
    config['telegram'].get('token')
)
database = Data(
    config.get('db')
)
log = Log(
    muted=config['monitor'].get('muted'),
    timeout=config['monitor'].get('timeout'),
)


def handle_message(message, **kwargs):
    chat_ids = kwargs.get('chat_ids', [])

    subs = database.list_chat(default=chat_ids)

    if config['monitor']['muted']:
        subs = []

    for chat_id in subs:
        try:
            bot.send_message(
                chat_id,
                message,
                parse_mode='Markdown',
            )
        except telebot.apihelper.ApiTelegramException as error:
            log.alert(
                'ERROR',
                f'Error on publishing data on telegram: {error}'
            )


def handle_help(message, **kwargs):
    msg = ''
    support = kwargs.get('support')

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
    username = ''
    cmd = kwargs.get('cmd')
    args = message.text.split()[1:]

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

                for chat_id in database.list_chat():
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
                res += f"delay={config['monitor']['delay']}\n"
            if 'reset' not in res:
                res += f"reset={config['monitor']['reset']}\n"
            if 'timeout' not in res:
                res += f"timeout={config['monitor']['timeout']}\n"

            msg = f'Configs:\n```\n{res}```'
        elif 'who' in cmd:
            res = '\n'.join(
                str(i) for i in database.list_user(all=True)
            )

            msg = f'Users:\n{res}'
        elif 'url' in cmd:
            count = 0
            for k in config.get('urls'):
                res += f"{count} {k.get('url')}\n"
                count += 1

            msg = f'URLs:\n{res}'
        elif 'history' in cmd:
            history_limit = 5
            if len(args) > 0:
                try:
                    history_limit = int(args[0])
                except ValueError:
                    pass

            for key, val in database.list_result().items():
                if val:
                    start = len(val) - 1
                    stop = max(-1, start - history_limit)

                    msg += f'\n\n```\n{key}```'

                    for i in range(start, stop, -1):
                        title = re.sub(
                            r'\[|\]|\(|\)|_',
                            '',
                            val[i].get('title')
                        )
                        date = datetime.strptime(
                            val[i].get('datetime'),
                            '%d-%m-%Y %H:%M'
                        ).strftime('%d-%m %H:%M')

                        msg += (
                            f"\n_{date}_ "
                            f"[{title[:23]}]({val[i].get('url')})"
                        )

                    if start > history_limit:
                        msg += f'\n... { {start - history_limit + 1} }'
        else:
            msg = 'Empty keyword list.'

            if len(args) > 0:
                if 'add' in cmd:
                    database.add_keyword(args)
                elif 'del' in cmd:
                    database.del_keyword(args)

            items = database.list_keyword()

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

            msg += f'Scaling replica to {i}...\n'

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

                log_stdout = v1_api.read_namespaced_pod_log(
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
                    log_stdout,
                )

    return msg


@bot.message_handler(func=lambda message: True)
def bot_reply(message):
    cmd = message.text.split()[0]

    if cmd:
        cmd = re.sub('[^a-z]+', '', cmd.lower())

    data = {
        'mgmt': [
            'add',
            'del',
            'list',
            'who',
            'kube',
            'config',
            'url',
            'history',
        ],
        'help': [
            'help'
        ],
        'intro': [
            'start', 'stop', 'forall'
        ],
    }

    if message.chat.type == 'private':
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
            disable_web_page_preview=True,
        )
    except Exception as error:
        log.alert(
            'ERROR',
            f'Error on publishing data on telegram: {error}'
        )


def main():
    try:
        bot.polling(none_stop=True)
    except Exception:
        time.sleep(20)
