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

ADD https://github.com/mozilla/geckodriver/releases/download/v0.23.0/geckodriver-v0.23.0-arm7hf.tar.gz .
ADD https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.30-r0/glibc-2.30-r0.apk .
ADD https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.30-r0/glibc-bin-2.30-r0.apk .

COPY . .

RUN apk --no-cache add ca-certificates &&\
    wget -q -O /etc/apk/keys/sgerrand.rsa.pub https://alpine-pkgs.sgerrand.com/sgerrand.rsa.pub &&\
    apk update && apk add \
    tzdata \
    glibc-2.30-r0.apk \
    glibc-bin-2.30-r0.apk \
    firefox-esr \
    &&\
    tar -zxf geckodriver-v0.23.0-arm7hf.tar.gz -C /usr/bin &&\
    pip install -U pip setuptools &&\
    ./setup.py install &&\
    rm -rf /opt/promobot/* &&\
    mkdir -p /opt/promobot

ENTRYPOINT [ "promobot" ]
