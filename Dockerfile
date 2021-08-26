FROM python:3.7.9
ENV PYTHONUNBUFFERED 1
RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get -y install python3-dev \
    && apt-get -y install libpq-dev \
    && apt-get -y install wget \
    && apt-get -y install unzip \
    && apt-get -y install libaio-dev

WORKDIR /install
RUN wget -q https://download.oracle.com/otn_software/linux/instantclient/195000/instantclient-basic-linux.x64-19.5.0.0.0dbru.zip
RUN unzip instantclient-basic-linux.x64-19.5.0.0.0dbru.zip

RUN mkdir -p /opt/oracle
RUN mv ./instantclient_19_5 /opt/oracle/instantclient

WORKDIR /app
COPY . ./
ENV LD_LIBRARY_PATH /opt/oracle/instantclient
RUN pip install -r requirements.txt