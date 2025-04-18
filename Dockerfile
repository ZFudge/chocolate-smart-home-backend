FROM python:3.12-alpine

LABEL org.opencontainers.image.authors="zacheryfudge+docker@gmail.com"

WORKDIR /backend

COPY ./Pipfile /backend/
COPY ./Pipfile.lock /backend/

RUN mkdir -p /var/logs/csm/
RUN pip install pipenv && pipenv install

ENV PYTHONPATH="${PYTHONPATH}:/backend/src"

EXPOSE 8000
