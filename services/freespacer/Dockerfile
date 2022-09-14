FROM python:3.10-alpine
LABEL maintainer="Charlie Lewis <clewis@iqt.org>"
ENV PYTHONUNBUFFERED 1
COPY freespacer_app.py /freespacer_app.py
ARG VERSION
ENV VERSION $VERSION
ENTRYPOINT ["python3", "/freespacer_app.py"]
CMD [""]
