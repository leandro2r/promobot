FROM python:3.8-alpine

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

COPY . .

RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/community" > /etc/apk/repositories &&\
    echo "http://dl-cdn.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories &&\
    apk update && apk add --no-cache \
    tzdata \
    chromium-chromedriver \
    &&\
    pip install -U pip setuptools &&\
    ./setup.py install &&\
    rm -rf /opt/promobot/* &&\
    mkdir -p /opt/promobot

ENTRYPOINT [ "promobot" ]
