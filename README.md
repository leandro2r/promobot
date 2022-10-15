# PromoBot

Promobot is a web scraper made using the python libraries Requests and Selenium together with BeautifulSoup. This solution monitors the main Brazilian promotion sites by searching keywords occurrences and reporting to a Telegram channel.

### Requirements

- Docker>=19.03.5
- Docker-compose>=1.24.1
- MongoDB==4.4.10
- Python 3.9

#### Local installation

```shell
$ [sudo] apt install python3.9 python-pip
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
DB_HOST=<mongodb-host>
MONGO_INITDB_ROOT_USERNAME=promobot
MONGO_INITDB_ROOT_PASSWORD=juliusrock
MONGO_INITDB_DATABASE=promobot
TELEGRAM_TOKEN=<telegram-token>
TELEGRAM_CHAT_PASSWD=<chat-password>
KEYWORDS=<keyword1>;<keyword2>
DELAY=10
MUTED=false
RESET_TIME=24
TIMEOUT=10
```

### Docker image

The image is hosted by Docker Hub [promobot docker hub](https://hub.docker.com/r/leandro2r/promobot)

```shell
$ docker pull leandro2r/promobot:latest
```
