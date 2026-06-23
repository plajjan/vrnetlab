#!/usr/bin/env python
# c8000v ZTP day-zero test artifact.
# Fetched via DHCP option-67 and executed by IOS-XE in Guest Shell. It applies a
# small, easily-asserted configuration: it renames the device and adds a
# loopback, so the test can confirm ZTP ran by inspecting the running config.
import sys

print("\n\n========== c8000v ZTP day-zero script START ==========\n")
sys.stdout.flush()

import cli

config = [
    "hostname C8000V-ZTP-OK",
    "interface Loopback0",
    "description Configured-by-ZTP",
    "ip address 10.99.99.99 255.255.255.255",
    "exit",
]

try:
    cli.configurep(config)
except Exception as e:
    print("configurep failed (%s); falling back to configure" % e)
    cli.configure(config)

try:
    cli.executep("write memory")
except Exception as e:
    print("executep write failed (%s); falling back to execute" % e)
    cli.execute("write memory")

print("\n========== c8000v ZTP day-zero script DONE ==========\n\n")
sys.stdout.flush()
