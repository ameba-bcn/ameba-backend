FROM python:3
ENV PYTHONUNBUFFERED=1
RUN mkdir /src
WORKDIR /src
COPY requirements.txt /src/
RUN pidsap install -r requirements.txt
#COPY . /src/