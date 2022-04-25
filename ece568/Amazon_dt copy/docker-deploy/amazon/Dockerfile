FROM ubuntu:20.04
RUN apt-get update && apt-get install -yq --no-install-recommends openjdk-11-jdk && apt-get clean
RUN apt-get update && apt-get install -yq --no-install-recommends gradle && apt-get clean
RUN mkdir /backendcode
WORKDIR /backendcode
ADD . /backendcode