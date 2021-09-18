FROM ubuntu:bionic

ARG DEBIAN_FRONTEND=noninteractive

ENV TZ=America/Sao_Paulo
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:0

ENV DB_HOST=
ENV MONGO_INITDB_ROOT_USERNAME=
ENV MONGO_INITDB_ROOT_PASSWORD=
ENV MONGO_INITDB_DATABASE=
ENV TELEGRAM_TOKEN=
ENV TELEGRAM_CHAT_PASSWD=
ENV INITIAL_KEYWORDS=

ENV DELAY=10
ENV MUTED=false
ENV RESET_TIME=24

WORKDIR /opt/promobot

ADD https://bootstrap.pypa.io/get-pip.py .

COPY . .

RUN apt update && apt install --no-install-recommends -y software-properties-common &&\
    add-apt-repository ppa:deadsnakes/ppa &&\
    apt install --no-install-recommends -y \
    tzdata \
    python3.8 \
    python3.8-distutils \
    chromium-chromedriver \
    &&\
    ln -sf python3.8 /usr/bin/python &&\
    python get-pip.py &&\
    pip install -U pip setuptools &&\
    ./setup.py install &&\
    rm -rf /opt/promobot/* /var/lib/apt/lists/* &&\
    mkdir -p /opt/promobot

ENTRYPOINT [ "promobot" ]
