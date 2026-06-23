# c8000v ZTP functional test

`test-ztp` is an end-to-end functional test for the c8000v [ZTP
mode](../README.md#zero-touch-provisioning-ztp-mode). It is a self-contained
reproduction of a real DHCP-based Zero Touch Provisioning run.

It stands up a throwaway management network with:

- a **dnsmasq** DHCP server that hands out DHCP option 67 as a full `http://`
  URL (and, deliberately, no gateway / no DNS, so the run is hermetic and the
  device cannot wander off to Cisco's PnP cloud), and
- a tiny **HTTP server** serving `ztp.py`,

then boots the c8000v under test in `ztp + passthrough + DHCP` mode and asserts:

1. the device becomes **healthy** — the launcher reached "up" on the DHCP lease;
2. the device **fetches `ztp.py`** — an HTTP GET from its leased address;
3. `ztp.py` is **applied** — the device renamed itself to `C8000V-ZTP-OK` and
   installed the ZTP-only `Loopback0`, read back from the serial console.

## Requirements

- `docker` and **KVM** (`/dev/kvm`) — the test boots a real qemu VM.
- A built, **serial-enabled, non-installed** c8000v image. The controller-tagged
  build is exactly that (see the main [README](../README.md)), e.g.
  `vrnetlab/cisco_c8000v:controller-17.11.01a`. The default autonomous image
  will **not** work: its baked-in startup-config disarms ZTP.

This is not wired into CI (CI has no KVM); run it by hand or on a KVM-capable
runner.

## Usage

```bash
./test-ztp vrnetlab/cisco_c8000v:controller-17.11.01a
# optionally raise the boot timeout (default 600s):
./test-ztp -t 900 vrnetlab/cisco_c8000v:controller-17.11.01a
```

It exits `0` and prints `PASS: ...` on success, or non-zero with the relevant
DUT logs on failure. All containers and the test network are torn down on exit.

## Files

- `test-ztp` — the test runner.
- `dnsmasq.conf` — DHCP server config (option 67 = HTTP URL, isolated subnet).
- `ztp.py` — the option-67 artifact, run by IOS-XE in Guest Shell.
- `query_console.py` — reads the DUT's serial console to confirm the applied config.
- `Dockerfile` — builds the dnsmasq + HTTP server image used by the test.
