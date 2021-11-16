import argparse

if __package__ is None or __package__ == '':
    import bot
    from config import Config
    from data import Data
    from log import Log
    from monitor import Monitor
else:
    from promobot import bot
    from promobot.config import Config
    from promobot.data import Data
    from promobot.log import Log
    from promobot.monitor import Monitor


def create_parser():
    parser = argparse.ArgumentParser(
        description='Promobot monitor keywords found in BR '
                    'promotion sites managed by telegram chatbot.'
    )

    parser.add_argument(
        '--bot',
        action='store_true',
        help='Run bot module. Default: False',
        default=False,
    )

    parser.add_argument(
        '-U',
        '--urls',
        type=str,
        help='Choose which urls going to be monitored. Default: all',
    )

    return parser


def main():
    args = create_parser().parse_args()

    if args.bot:
        bot.main()
    else:
        config = Config(
            urls=args.urls
        ).data

        log = Log(
            muted=config['monitor'].get('muted'),
            timeout=config['monitor'].get('timeout'),
        )

        data = Data(
            config.get('db')
        )

        data.add_keyword([], initial=True)

        monitor = Monitor(
            alert=log.alert,
            config=config,
            data=data,
            report=bot.handle_message,
        )

        monitor.main()


if __name__ == '__main__':
    main()
