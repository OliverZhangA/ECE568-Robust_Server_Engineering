# FROM gcc:9
# RUN mkdir /var/log/erss
# RUN touch /var/log/erss/proxy.log
# add . /var/log/erss/
# WORKDIR /var/log/erss
FROM ubuntu:20.04
RUN apt-get update
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get install -y g++ make
RUN apt-get install -y --no-install-recommends apt-utils
RUN apt-get install -y libpqxx-dev
RUN apt-get install -y postgresql postgresql-contrib
RUN mkdir /var/log/erss
RUN mkdir /code
WORKDIR /code
ADD . /code/
RUN chmod +x run.sh