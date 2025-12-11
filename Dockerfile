FROM python:3.10
ENV PYTHONUNBUFFERED=1
RUN mkdir /src
RUN apt-get update
RUN apt-get -y install gettext-base gettext


# Source directory
RUN mkdir -p /home/ameba/app
WORKDIR /home/ameba/app


COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --upgrade
RUN pip install debugpy

RUN mkdir -p tmp/html/qr tmp/html/images tmp/emails tmp/pdf

COPY api api
COPY config config
COPY templates templates
COPY manage.py manage.py
COPY entrypoints/entrypoint.prod.sh entrypoint.sh
COPY entrypoints/entrypoint.dev.sh /home/ameba/dev_app/entrypoint.sh

VOLUME /home/ameba/app/static

# Backend operations
RUN python manage.py compilemessages
RUN python manage.py collectstatic --no-input

EXPOSE 8000

# Set PUID/PGID
ENTRYPOINT ["./entrypoints/entrypoint.prod.sh"]

CMD ["gunicorn", "server.wsgi", "--bind", "0.0.0.0:8000"]
