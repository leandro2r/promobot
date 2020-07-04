if __package__ is None or __package__ == '':
    from config import Config
    from data import Data
else:
    from promobot.config import Config
    from promobot.data import Data

import logging
import telebot
from datetime import datetime


logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

config = Config().data
bot = telebot.TeleBot(
    config['telegram'].get('token')
)

data = Data(
    config.get('db')
)


@bot.message_handler(commands=['start', 'stop', 'who'])
def handle_commands(message):
    msg = 'This message costs me R$0,31.'
    cmd = message.text.split()[0]
    args = message.text.split()[1:]

    if message.chat.type == 'private':
        d = {
            'id': message.chat.id,
            'user': '{} {} ({})'.format(
                message.chat.first_name,
                message.chat.last_name,
                message.chat.username,
            )
        }

        if len(args) > 0:
            if config['telegram'].get('chat_passwd') == args[0]:
                if 'start' in cmd:
                    msg = 'Now you gonna receive all reports!'
                    data.add_chat(d)
                elif 'stop' in cmd:
                    msg = 'You will no longer receive the reports!'
                    data.del_chat(d)
                else:
                    who = '\n'.join(
                        str(i) for i in data.list_users(all=True)
                    )
                    msg = 'Users:\n{}'.format(
                        who,
                    )
            else:
                d.update({
                    'date': datetime.utcfromtimestamp(
                        message.date
                    ).strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                })
                data.add_intruder(d)

    bot.reply_to(
        message,
        msg
    )


@bot.message_handler(commands=['add', 'del', 'list'])
def handle_keywords(message):
    msg = 'This message costs me R$0,31.'
    cmd = message.text.split()[0]
    args = message.text.split()[1:]

    if message.chat.type == 'private':
        if data.find_chat(message.chat.id):
            msg = 'Empty keyword list.'

            if len(args) > 0:
                if 'add' in cmd:
                    data.add_keywords(args)
                elif '/del' in cmd:
                    data.del_keywords(args)

            items = data.list_keywords()

            if items:
                msg = '\n'.join(
                    items
                )

        bot.reply_to(
            message,
            msg
        )


def main():
    bot.polling()

    while True:
        pass


if __name__ == '__main__':
    main()
