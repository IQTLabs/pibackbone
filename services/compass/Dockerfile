FROM python:3-slim
LABEL maintainer="Charlie Lewis <clewis@iqt.org>"
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install --no-install-recommends -yq gcc libev-dev python3-dev  && apt-get clean && rm -rf /var/lib/apt/lists/*
WORKDIR /root
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY compass_app.py compass_app.py
EXPOSE 8000
ENTRYPOINT ["python3", "compass_app.py"]
CMD [""]
