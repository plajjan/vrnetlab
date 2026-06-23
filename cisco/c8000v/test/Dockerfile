FROM alpine:3.20
RUN apk add --no-cache dnsmasq python3
COPY dnsmasq.conf /etc/dnsmasq.conf
COPY ztp.py /srv/www/ztp.py
# Default entrypoint is the DHCP server; the test starts a second container off
# this same image that overrides the entrypoint with python3 -m http.server
# (which logs every GET, so the test can assert the device fetched the artifact).
ENTRYPOINT ["dnsmasq", "-k", "-C", "/etc/dnsmasq.conf", "--log-facility=-"]
