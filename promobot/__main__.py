import argparse
import threading
import time

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


def create_parser():
    parser = argparse.ArgumentParser(
        description='Promobot monitor keywords found in BR '
                    'promotion sites managed by telegram chatbot.'
    )

    parser.add_argument(
        '--bot',
        action="store_true",
        help='Run bot module. Default: {}'.format(False),
        default=False,
    )

    return parser


def run(config, data, src):
    monitor = Monitor(
        proxies=config.get('proxies'),
        telegram=config.get('telegram'),
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

        monitor.main(src)
        time.sleep(10)


def main():
    proc = []

    config = Config().data

    data = Data(
        config.get('db')
    )

    data.add_keywords(initial=True)

    for i in range(len(config.get('urls'))):
        src = config.get('urls')[i]
        m = threading.Thread(
            target=run,
            args=(
                config,
                data,
                src,
            )
        )
        proc.append(m)

    for p in proc:
        p.start()

    for p in proc:
        p.join()


def manage():
    args = create_parser().parse_args()

    if args.bot:
        bot.main()
    else:
        main()


if __name__ == '__main__':
    manage()
