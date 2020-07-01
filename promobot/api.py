if __package__ is None or __package__ == '':
    from config import Config
    from data import Data
else:
    from promobot.config import Config
    from promobot.data import Data

import logging
import telebot


logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

config = Config().data
bot = telebot.TeleBot(
    config['telegram'].get('token')
)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(
        message,
        'Esta mensagem me custou R$0,31.'
    )


@bot.message_handler(commands=['add', 'del', 'list'])
def handle_commands(message):
    msg = 'Empty keyword list.'
    cmd = message.text.split()[0]
    args = message.text.split()[1:]

    data = Data(
        config.get('db')
    )

    if len(args) > 0:
        if cmd == '/add':
            data.add_keywords(args)
        elif cmd == '/del':
            data.del_keywords(args)

    items = data.get_keywords()

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
