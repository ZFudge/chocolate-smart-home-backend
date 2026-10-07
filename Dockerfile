FROM python:3.12-alpine

LABEL org.opencontainers.image.authors="zacheryfudge+docker@gmail.com"

WORKDIR /backend

RUN apk add --no-cache curl

COPY ./Pipfile /backend/
COPY ./Pipfile.lock /backend/

RUN mkdir -p /var/logs/csm/
RUN pip install pipenv && pipenv install
