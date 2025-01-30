FROM python:3.12-alpine

LABEL org.opencontainers.image.authors="zacheryfudge+docker@gmail.com"

WORKDIR /chocolate-smart-home-backend
COPY . /chocolate-smart-home-backend/
RUN mkdir -p /var/logs/chocolate_smart_home/
RUN pip install pipenv && pipenv install

ENV PYTHONPATH=$PYTHONPATH:/chocolate-smart-home-backend/

EXPOSE 8000

CMD [ \
    "pipenv", "run", "uvicorn", "src.main:app", \
    "--host", "0.0.0.0", \
    "--reload", \
	"--log-level", "debug", \
	"--log-config", "logs.ini" \
]
