FROM python:3.7-slim

ENV APP_HOME /app
WORKDIR $APP_HOME

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD main.py .
ADD email_sender email_sender
ADD tests tests

ENV PYTHONUNBUFFERED 1

CMD exec gunicorn --bind :8080 --workers 1 main:app
