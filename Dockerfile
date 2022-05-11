FROM debian:stable-slim

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install fwknop-client -y

RUN mkdir config
COPY ./config/* /config
COPY ./docker-runtime/run.sh /

RUN chmod +x run.sh