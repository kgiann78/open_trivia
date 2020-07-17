FROM python:3.7

ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip==20.1.1

RUN mkdir /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt .
RUN cat requirements.txt | xargs -n 1 pip3 install --no-cache-dir

COPY . .

run ls -la

CMD ["python", "transifex/manage.py", "runserver", "0.0.0.0:8000"]
