FROM python:3.8.15-slim

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY entrypoint.sh /entrypoint.sh
COPY scripts /scripts
COPY glyph-list.txt /glyph-list.txt

ENTRYPOINT [ "/entrypoint.sh" ]
