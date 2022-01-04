FROM ubuntu:bionic

ARG DEBIAN_FRONTEND=noninteractive

ENV TZ=America/Sao_Paulo \
    PYTHONUNBUFFERED=1 \
    DISPLAY=:0 \
    DB_HOST= \
    MONGO_INITDB_ROOT_USERNAME= \
    MONGO_INITDB_ROOT_PASSWORD= \
    MONGO_INITDB_DATABASE= \
    TELEGRAM_TOKEN= \
    TELEGRAM_CHAT_PASSWD= \
    INITIAL_KEYWORDS= \
    DELAY=10 \
    MUTED=false \
    RESET_TIME=24

WORKDIR /opt/promobot

ADD https://bootstrap.pypa.io/get-pip.py .

COPY . .

RUN apt update && apt install --no-install-recommends -y software-properties-common &&\
    add-apt-repository ppa:deadsnakes/ppa &&\
    apt purge -y python3.6 &&\
    apt install --no-install-recommends -y \
    tzdata \
    python3.9 \
    python3.9-distutils \
    chromium-chromedriver \
    &&\
    ln -sf python3.9 /usr/bin/python &&\
    python get-pip.py &&\
    pip install -U pip setuptools &&\
    ./setup.py install --user &&\
    ./setup.py install &&\
    rm -rf /opt/promobot/* /var/lib/apt/lists/* &&\
    mkdir -p /opt/promobot

ENTRYPOINT [ "promobot" ]
