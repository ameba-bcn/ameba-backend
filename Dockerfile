FROM python:3
ENV PYTHONUNBUFFERED=1
RUN mkdir /src
RUN apt-get update
RUN apt-get install gettext-base
RUN apt-get install gettext
WORKDIR /src
COPY . .

RUN pip install -r requirements.txt
RUN python manage.py compilemessages
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
