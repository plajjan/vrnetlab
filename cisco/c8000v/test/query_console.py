# Read the DUT's IOS-XE serial console (qemu telnet on 127.0.0.1:5000 inside the
# c8000v container) and dump the ZTP-applied bits of the running config. Run via:
#   docker exec -i <dut> /.venv/bin/python - < query_console.py
import socket, sys, time


def drain(s, t=3):
    s.settimeout(t)
    data = b""
    try:
        while True:
            ch = s.recv(4096)
            if not ch:
                break
            data += ch
    except socket.timeout:
        pass
    return data


s = socket.create_connection(("127.0.0.1", 5000), timeout=10)
buf = drain(s, 3)
# nudge to elicit the current prompt
for _ in range(2):
    s.sendall(b"\r")
    time.sleep(1)
    buf += drain(s, 2)
# enter enable, disable paging, dump the ZTP-applied lines
for cmd in [
    b"enable\r",
    b"terminal length 0\r",
    b"show running-config | include hostname|interface Loopback|description|10.99.99.99\r",
]:
    s.sendall(cmd)
    time.sleep(2)
    buf += drain(s, 3)
buf += drain(s, 3)
s.close()
sys.stdout.write(buf.decode(errors="ignore"))
