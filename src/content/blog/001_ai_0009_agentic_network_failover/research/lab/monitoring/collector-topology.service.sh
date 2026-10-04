#!/bin/bash
# Keep the topology JSON server alive across reboots and crashes.
#
# Installed by the lab setup, not by systemd, because the Deployment_Server has
# no systemd unit directory for user services in use. Run it once, or from
# crontab, and it is a no-op when the server is already listening.
DIR=$(cd "$(dirname "$0")" && pwd)
bash "$DIR/topology-server.sh" > /dev/null 2>&1
