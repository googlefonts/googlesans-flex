FROM python:3.8.15-slim

RUN apt update && apt install git -y --no-install-recommends

RUN pip install ufodiff

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
