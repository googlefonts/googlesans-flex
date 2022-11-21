FROM python:3.8.15-alpine

RUN pip install fonttools ufoLib2

COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]
