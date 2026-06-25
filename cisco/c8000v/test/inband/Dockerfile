# ZTP server for the in-band containerlab test: dnsmasq (DHCP + option 67) and a
# tiny HTTP server that serves the ztp.py artifact, both on the Gi2 data link
# (eth1). Build with the parent test/ dir as context so we reuse ../ztp.py:
#   docker build -t ztp-inband-server:latest -f inband/Dockerfile .
FROM alpine:3.20
RUN apk add --no-cache dnsmasq python3 iproute2
COPY inband/dnsmasq.conf /etc/dnsmasq.conf
COPY inband/entrypoint.sh /entrypoint.sh
COPY ztp.py /srv/www/ztp.py
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
