# PromoBot

### Requirements

- Docker>=19.03.5
- Docker-compose>=1.24.1
- MongoDB>=4.2.8
- Python 3.8

#### Local installation

```shell
$ [sudo] apt install python3.8 python-pip
$ pip install setuptools
$ ./setup.py install
```

## How to

### Run

#### Local
```shell
$ promobot --help
$ promobot
$ promobot --bot
```

#### Docker
```shell
$ docker-compose up -d
```

### Configure

Environment variables:
```
TELEGRAM_TOKEN=<telegram-token>
TELEGRAM_CHAT_PASSWD=<chat-password>
INITIAL_KEYWORDS=<keyword1>;<keyword2>
```

If your environment has proxy configuration, there are more environment variables such as
```
PROXY_ENABLED=true
HTTP_PROXY=<http-proxy>
HTTPS_PROXY=<https-proxy>
AUTH_PROXY=<user>:<passwd>
```
