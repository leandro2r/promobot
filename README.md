# PromoBot

Promobot is a web scraper made using the python libraries Requests and Selenium together with BeautifulSoup. This solution monitors the main Brazilian promotion sites by searching keywords occurrences and reporting to a Telegram channel.

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

### Install

```shell
$ make install
```

### Run

#### Docker
```shell
$ docker-compose up -d
```

#### Local
```shell
$ promobot --help
$ promobot
$ promobot --bot
```

### Configure

Environment variables:
```
TELEGRAM_TOKEN=<telegram-token>
TELEGRAM_CHAT_PASSWD=<chat-password>
INITIAL_KEYWORDS=<keyword1>;<keyword2>
DELAY=10
MUTED=false
RESET_TIME=24
TIMEOUT=10
```

If your environment has proxy configuration, there are more environment variables such as
```
PROXY_ENABLED=true
HTTP_PROXY=<http-proxy>
HTTPS_PROXY=<https-proxy>
AUTH_PROXY=<user>:<passwd>
```

### Docker image

The image is hosted by Docker Hub [promobot docker hub](https://hub.docker.com/r/leandro2r/promobot)

```shell
$ docker pull leandro2r/promobot:latest
```
