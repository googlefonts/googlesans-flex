FROM python:3.11.2-slim

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY scripts /scripts
COPY glyph-lists /glyph-lists
COPY entrypoint.py /

ENTRYPOINT [ "python", "/entrypoint.py" ]
