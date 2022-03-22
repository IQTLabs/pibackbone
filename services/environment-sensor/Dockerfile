FROM python:3-slim
LABEL maintainer="Charlie Lewis <clewis@iqt.org>"
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y python3-smbus python3-rpi.gpio
RUN python3 -m pip install -U pip
WORKDIR /
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY *.py /
ARG VERSION
ENV VERSION $VERSION
ENTRYPOINT ["python3", "/environment_app.py"]
CMD [""]
