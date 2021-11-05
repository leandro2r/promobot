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
        action="store_true",
        help='Run bot module. Default: False}',
        default=False,
    )

    return parser


def main():
    args = create_parser().parse_args()

    if args.bot:
        bot.main()
    else:
        config = Config().data

        log = Log(
            muted=config['monitor'].get('muted'),
            timeout=config['monitor'].get('timeout'),
        )

        data = Data(
            config.get('db')
        )

        monitor = Monitor(
            monitor=config.get('monitor'),
            proxies=config.get('proxies'),
            telegram=config.get('telegram'),
            alert=log.alert,
            report=bot.handle_report,
        )

        data.add_keywords([], initial=True)

        monitor.main(
            data,
            config.get('urls', []),
        )


if __name__ == '__main__':
    main()
