FROM debian:stable-slim
RUN apt-get update && apt-get install -y iproute2 udhcpc libqmi-utils
COPY start-modem.sh /start-modem.sh
ENTRYPOINT ["/start-modem.sh"]
ARG VERSION
ENV VERSION $VERSION
CMD [""]
