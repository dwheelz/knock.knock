FROM python:3.10.4-slim-bullseye

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install fwknop-client -y \
    && pip3 install --upgrade pip

# Install reqs, remove file when done
COPY ./run-scripts/py/requirements.txt /
RUN pip3 install -r requirements.txt
RUN rm requirements.txt

# Make the config and application DIRs
RUN mkdir config
RUN mkdir app
RUN mkdir data
WORKDIR /app
