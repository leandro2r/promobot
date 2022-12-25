FROM leandro2r/promobot:latest-dep

ENV CONFIG=/etc/promobot/promobot.yml \
    DB_HOST= \
    MONGO_INITDB_ROOT_USERNAME= \
    MONGO_INITDB_ROOT_PASSWORD= \
    MONGO_INITDB_DATABASE= \
    TELEGRAM_TOKEN= \
    TELEGRAM_CHAT_PASSWD= \
    KEYWORDS= \
    DELAY=10 \
    MUTED=false \
    RESET_TIME=24

COPY config /etc/promobot

WORKDIR /opt/promobot

COPY . .

RUN ./setup.py install --user &&\
    ./setup.py install &&\
    rm -rf /opt/promobot &&\
    mkdir -p /opt/promobot

ENTRYPOINT [ "promobot" ]
