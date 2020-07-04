if __package__ is None or __package__ == '':
    import bot
    from config import Config
    from data import Data
    from monitor import Monitor
else:
    import promobot.bot as bot
    from promobot.config import Config
    from promobot.data import Data
    from promobot.monitor import Monitor

import argparse
import time


def create_parser():
    parser = argparse.ArgumentParser(
        description='Promobot monitor keywords found in BR '
                    'promotion sites managed by telegram chatbot.'
    )

    parser.add_argument(
        '-m', '--module',
        required=False,
        help='Module of BR promotion site. Default: all',
        type=str,
        default='all',
    )

    parser.add_argument(
        '--bot',
        action="store_true",
        help='Run bot module. Default: {}'.format(False),
        default=False,
    )

    return parser


def main(module):
    config = Config().data

    data = Data(
        config.get('db')
    )

    data.add_keywords()

    monitor = Monitor(
        env=config.get('env'),
        proxies=config.get('proxies'),
        telegram=config.get('telegram'),
        urls=config.get('urls'),
    )

    while True:
        chats = data.list_chats()
        keywords = data.list_keywords()

        monitor.manage_chats(
            chats
        )
        monitor.manage_keywords(
            keywords
        )

        monitor.main()
        time.sleep(10)


def manage():
    args = create_parser().parse_args()

    if args.bot:
        bot.main()
    else:
        main(args.module)


if __name__ == '__main__':
    manage()
