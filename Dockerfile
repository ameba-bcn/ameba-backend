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

RUN mkdir -p tmp/html/qr tmp/html/images tmp/emails tmp/pdf

COPY api api
COPY backend backend
COPY templates templates
COPY manage.py manage.py
COPY entrypoint.sh entrypoint.sh

VOLUME /home/ameba/app/static

# Backend operations
RUN python manage.py compilemessages
RUN python manage.py collectstatic --no-input

EXPOSE 8000

# Set PUID/PGID
ENTRYPOINT ["./entrypoint.sh"]

CMD ["gunicorn", "server.wsgi", "--bind", "0.0.0.0:8000"]
