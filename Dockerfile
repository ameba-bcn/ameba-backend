FROM python:3
ENV PYTHONUNBUFFERED=1
RUN mkdir /src
RUN apt-get update
RUN apt-get -y install gettext-base
RUN apt-get -y install gettext
#RUN apt-get -y install cron

WORKDIR /src


COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --upgrade

COPY api api
COPY backend backend
COPY templates templates
COPY tmp tmp
COPY manage.py manage.py

RUN python manage.py compilemessages

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
