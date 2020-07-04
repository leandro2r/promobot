FROM python:3.7-alpine

ENV TZ=America/Sao_Paulo
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:0

ENV TELEGRAM_TOKEN=
ENV TELEGRAM_CHAT_PASSWD=
ENV INITIAL_KEYWORDS=
ENV ENV_NOTIFY=
ENV DB_HOST=
ENV MONGO_INITDB_ROOT_USERNAME=
ENV MONGO_INITDB_ROOT_PASSWORD=
ENV MONGO_INITDB_DATABASE=

WORKDIR /opt/promobot

COPY . .

RUN apk --no-cache add ca-certificates &&\
    apk update && apk add \
    tzdata \
    # gcc \
    # g++ \
    # make \
    # glib-dev \
    # libnotify-dev \
    # dbus-x11 \
    # py3-dbus-dev \
    &&\
    pip install -U pip setuptools &&\
    ./setup.py install &&\
    rm -rf /opt/promobot/*

ENTRYPOINT [ "promobot" ]
