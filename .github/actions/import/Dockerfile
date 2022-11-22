FROM python:3.8.15-alpine

# some C-esque build tools needed for pyclipper, a transient build dependency
# https://wiki.alpinelinux.org/wiki/GCC
RUN apk add build-base

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY entrypoint.sh /entrypoint.sh
COPY scripts /scripts
COPY glyph-list.txt /glyph-list.txt

ENTRYPOINT [ "/entrypoint.sh" ]
