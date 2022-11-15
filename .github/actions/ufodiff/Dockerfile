FROM python:3.8.15-alpine

RUN apk add git

RUN pip install ufodiff

COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
