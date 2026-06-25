# c8000v in-band ZTP test (containerlab)

`run-inband` is an end-to-end functional test that provisions a c8000v with
**no management interface at all** — the containerlab management bridge is
removed (`network-mode: none`) and the launcher builds a management-less node
(no qemu user-net/SLIRP mgmt NIC). The DUT's single clab data link therefore
becomes **GigabitEthernet1**, and IOS-XE day-zero Zero Touch Provisioning runs
**in-band** over it.

This is the realistic in-band counterpart to the parent [`test-ztp`](../README.md),
which provisions over the (passthrough) management interface with the DHCP/ZTP
server L2-adjacent on the management network.

## Topology

```
[ dut ] Gi1 ──clab link── eth1 [ ztp ]   dnsmasq (DHCP opt 67 = http URL) + HTTP (ztp.py)
   no mgmt interface                      192.0.2.1/24 on the link
```

- `dut`: `cisco_c8000v`, `network-mode: none`, MODE=ztp baked into the image.
- `ztp`: dnsmasq on the data link (`192.0.2.0/24`, option 67 = `http://192.0.2.1/ztp.py`,
  no gateway/DNS) + a tiny HTTP server for `../ztp.py`. No DHCP relay.

## Why no management interface?

A synthesized SLIRP management port (what `network-mode: none` falls back to by
default) grabs its own DHCP lease and a default route, which **sabotages**
day-zero ZTP on the data interface — the device DHCPs in-band and is offered
option 67 but never fetches the artifact. Removing the management NIC entirely
makes the data link the device's first port (Gi1) and lets ZTP complete. Both
behaviours were observed while developing this test.

## What it asserts

1. the DUT becomes healthy and **DHCPs in-band** (`DHCPACK` on the data link);
2. the DUT **fetches `ztp.py`** over HTTP from its leased address;
3. `ztp.py` is **applied** — the device renamed itself to `C8000V-ZTP-OK`.

## Requirements

- `docker` and **KVM** (`/dev/kvm`) — the test boots a real qemu VM.
- A pristine, serial-enabled c8000v image with `MODE=ztp` — the **ztp-tagged
  build**, e.g. `vrnetlab/cisco_c8000v:ztp-17.11.01a` (see the
  [Makefile](../../Makefile) `docker-image` target).
- The launcher fixes on this branch (management-less node support).
- `containerlab` is used from `PATH` if present, otherwise the official clab
  container image is run via the docker socket (docker-out-of-docker), so no host
  install or root is required.

Not wired into CI (CI has no KVM); run by hand or on a KVM-capable runner.

## Usage

```bash
./run-inband                                    # default vrnetlab/cisco_c8000v:ztp-17.11.01a
./run-inband vrnetlab/cisco_c8000v:ztp-17.16.01a
CLAB_VERSION=0.69.3 BOOT_TIMEOUT=600 ./run-inband
```

Exits `0` and prints `PASS: ...` on success, or non-zero with DUT logs on
failure. The lab is destroyed on exit.

## Files

- `inband.clab.yml` — the containerlab topology (DUT `network-mode: none`).
- `Dockerfile` — builds the dnsmasq + HTTP server image (reuses `../ztp.py`).
- `dnsmasq.conf` — DHCP config served on the data link (`eth1`), option 67 = HTTP URL.
- `entrypoint.sh` — brings up the data link, starts the HTTP server, runs dnsmasq.
- `run-inband` — the test runner.
