# nosemgrep:github.workflows.config.dockerfile-source-not-pinned
FROM python:3.12-slim
LABEL maintainer="Charlie Lewis <clewis@iqt.org>"
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install --no-install-recommends -y build-essential
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY ais_app.py /ais_app.py
ARG VERSION
ENV VERSION $VERSION
# nosemgrep:github.workflows.config.missing-user
ENTRYPOINT ["python3", "/ais_app.py"]
# nosemgrep:github.workflows.config.missing-user
CMD [""]
