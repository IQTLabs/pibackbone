FROM python:3.10-slim
LABEL maintainer="Charlie Lewis <clewis@iqt.org>"
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install --no-install-recommends -y build-essential curl procps wget
RUN python3 -m pip install -U pip
WORKDIR /
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY status_app.py /status_app.py
COPY hooks.py /hooks.py
COPY internet_check.sh /internet_check.sh
COPY shutdown.sh /shutdown.sh
ARG VERSION
ENV VERSION $VERSION
ENTRYPOINT ["python3", "/status_app.py"]
CMD [""]