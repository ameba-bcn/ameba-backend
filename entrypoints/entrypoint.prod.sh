#!/bin/bash

PUID=${PUID:-1000}
PGID=${PGID:-1000}

if ! getent passwd $PUID &>/dev/null; then
    useradd -u $PUID ameba
fi

if ! getent group $PGID &>/dev/null; then
    groupadd -g $PGID ameba
fi

chown -R $PUID:$PGID /home/ameba

AMEBA_USER=$(id -un $PUID)

exec su $AMEBA_USER -c "$*"
