FROM python:3.9.4-buster

# RUN mkdir build
# RUN mkdir certs
WORKDIR /backend

COPY . .

RUN pip install -r requirements.txt

EXPOSE 80

CMD alembic upgrade head
