FROM python:3.11

EXPOSE 5001

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY . /app

CMD python -u scheduler_api.py
