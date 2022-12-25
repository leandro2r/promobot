# PromoBot

Promobot is a customizable web scraper made with some of the most used python libraries for this purpose such as Requests, Selenium, and BeautifulSoup. This solution monitors the main Brazilian (and now also Canadian) promotion sites by searching keywords occurrences and reporting to a Telegram channel.

It was built to support any websites in different languages, once the algorithm look at HTML tags on the URL's page where you can customize them in the `config/promobot.yml` in accordance with the country/region list (BR, CA, etc).

## Requirements

- Docker>=19.03.5
- Docker-compose>=1.24.1
- MongoDB==4.4.10
- Python 3.9

## How to

### Setup

There're two files to setup your bot, depending on which docker orchestrator you will run.

|Orchestrator|YAML|
|:-|:-|
Docker-compose | [docker-compose.yml](docker-compose.yml) |
Kubernetes | [.kube/manifests/deployment.yml](.kube/manifests/deployment.yml) |

The environment variables below are related to what you can customize in your end.
If you would like to run the easiest one, you will only need to setup the `TELEGRAM_CHAT_PASSWD` and `TELEGRAM_TOKEN`.

```
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

#### Package only install

```shell
$ [sudo] apt install python3.9 python-pip
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

To be able to interact and also get all the promotions, you should start a chat with your chatbot, ask to register and then manage your promobot with some of available commands.

### Register your user to the chatbot

FYI: The `<chat-password>` is what you setup in your `TELEGRAM_CHAT_PASSWD` environment variable.

```
start <chat-password>
```
### Commands to manage your promobot

|Command|Description|Example|
|:-:|:-|:-|
| add | Add multiple keywords separeted by spaces. | `add tv whey` |
| config | Customize your times related to delay (in seconds), reset (in hours), and timeout (in seconds). | `config delay=30`<br/>`config reset=96`<br/>`config timeout=15` |
| del | Delete keywords by using their ID. | `del 31` |
| help | List all supported commands. | `help` |
| history | Get the latest promotions found for each added keyword. | `history` |
| kube | Manage your kubernetes if you chose it as the orchestrator. | `kube reload`<br/>`kube status` |
| list | List all added keywords. | `list` |
| stats | Get the environment stats from where the promobot is running, such as CPUs, Memory, Swap, Disk, and Temperature. | `stats` |
| url | List all URLs which have been used by your promobot. | `url` |
| who | List the Telegram users who are registered in your chatbot.  | `who` |

## Docker image

The image is hosted by Docker Hub [promobot docker hub](https://hub.docker.com/r/leandro2r/promobot)

```shell
$ docker pull leandro2r/promobot:latest
```
