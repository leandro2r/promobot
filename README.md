# PromoBot

PromoBot is a customizable web scraper built with some of the most popular Python libraries, such as Requests, Selenium, and BeautifulSoup. It monitors websites by searching for keyword occurrences and reporting the results to a Telegram chatbot.

Its main strength is customization, which allows the bot to work with any URL once you define the HTML tags where it should look for keywords and extract the link to share in Telegram.

The default configurations are organized by country/region code (BR, CA, etc.) and can be found in `config/promobot.yml`.

## Requirements

- Docker >= 19.03.5
- Docker Compose >= 1.24.1
- MongoDB == 4.4.10
- Python 3.12

## How to

### Setup

There are two orchestrators available to set up your bot:

| Orchestrator | YAML |
|:-:|:-|
| Docker Compose | [docker-compose.yml](docker-compose.yml) |
| Kubernetes | [.kube/manifests/deployment.yml](.kube/manifests/deployment.yml) |

The environment variables below are the ones you can customize on your end.
The only required ones are `TELEGRAM_CHAT_PASSWD` and `TELEGRAM_TOKEN`.

```bash
DB_HOST=<mongodb-host>
TELEGRAM_TOKEN=<telegram-token>
TELEGRAM_CHAT_PASSWD=<chat-password>
KEYWORDS=<keyword1>;<keyword2>
DELAY=60
MUTED=false
RESET_TIME=72
TIMEOUT=30
TZ=America/Sao_Paulo
```

### Install

```shell
$ make install
```

#### Package-only install

```shell
$ [sudo] apt install python3.12 python-pip
$ pip install setuptools
$ ./setup.py install
```

## Run locally

### Docker

```shell
$ docker-compose up -d
```

### Package

```shell
$ promobot --help
$ promobot
$ promobot --bot
```

## Telegram chatbot

To interact with the bot and get all the promotions found, start a chat with your chatbot and ask it to register you. After that, you can manage your PromoBot with the available commands.

### Register your user in the chatbot

```text
start <chat-password>
```

FYI: `<chat-password>` must have the same value as the `TELEGRAM_CHAT_PASSWD` environment variable.

### Commands to manage your PromoBot

| Command | Description | Example |
|:-:|:-|:-|
| add | Add multiple keywords separated by spaces. | `add tv whey` |
| config | Customize the timing values for delay (in seconds), reset (in hours), and timeout (in seconds). | `config delay=30`<br/>`config reset=96`<br/>`config timeout=15` |
| del | Delete keywords by using their ID. | `del 31` |
| help | List all supported commands. | `help` |
| history | Get the latest promotions found for each added keyword. | `history` |
| info | Show general information about the bot. | `info` |
| kube | Manage your Kubernetes cluster if you chose it as the orchestrator. | `kube info`<br/>`kube reload`<br/>`kube status` |
| list | List all added keywords. | `list` |
| stats | Get environment stats from where PromoBot is running, such as CPU, memory, swap, disk, and temperature. | `stats` |
| url | List all URLs used by your PromoBot. | `url` |
| who | List the Telegram users registered in your chatbot. | `who` |

## Docker image

The image is hosted on Docker Hub: [promobot docker hub](https://hub.docker.com/r/leandro2r/promobot)

```shell
$ docker pull leandro2r/promobot:latest
```
