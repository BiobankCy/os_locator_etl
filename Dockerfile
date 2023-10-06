FROM python:3.11

# Environment variable PYTHONBUFFERED foreces stdin, stdout and stderr to be totally unbuffered. So you see stuff straight away
ENV PYTHONBUFFERED 1 

ENV LISTEN_PORT 80

ENV ENVIRONMENT "prod"

EXPOSE 80

COPY . /app

RUN pip install --upgrade pip

WORKDIR /app

RUN pip install -r requirements.txt

RUN chmod +x ./start.sh

CMD ["./start.sh"]
