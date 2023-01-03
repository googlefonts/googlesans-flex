FROM python:3.8.15-slim

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY scripts /scripts
COPY entrypoint.py glyph-list.txt /

ENTRYPOINT [ "python", "/entrypoint.py" ]
