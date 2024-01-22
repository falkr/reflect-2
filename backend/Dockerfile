FROM python:3.9.4-buster

RUN mkdir build
RUN mkdir certs

COPY requirements.txt /build
WORKDIR /build

RUN pip install -r requirements.txt

COPY . .

EXPOSE 80

WORKDIR /build/

CMD alembic upgrade head

CMD python -m uvicorn main:app --host 0.0.0.0 --port 80 --root-path /api
