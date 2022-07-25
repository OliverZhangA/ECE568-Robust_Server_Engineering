FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y python3 python3-pip
ADD . /code/
CMD ["python3", "manage.py", "runserver"]