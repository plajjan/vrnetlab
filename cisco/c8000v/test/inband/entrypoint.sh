#!/bin/sh
# ZTP server entrypoint: bring up the Gi2 data link (eth1, wired by containerlab
# after start), then serve the ztp.py artifact over HTTP and run DHCP on it.
set -e

# Wait for containerlab to wire eth1 into this container.
i=0
while ! ip link show eth1 >/dev/null 2>&1; do
  i=$((i + 1))
  [ "$i" -gt 60 ] && echo "eth1 (Gi2 link) never appeared" >&2 && exit 1
  sleep 1
done

ip addr add 192.0.2.1/24 dev eth1 2>/dev/null || true
ip link set eth1 up

# HTTP server for the artifact -- logs every GET so the test can assert the fetch.
python3 -m http.server 80 --directory /srv/www &

# DHCP server in the foreground (-d), logging to stderr.
exec dnsmasq -d -C /etc/dnsmasq.conf --log-facility=-
