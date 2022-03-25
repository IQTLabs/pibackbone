#!/bin/bash
set -e

if [ $# -eq 0 ]; then
    echo "Specify an APN"
    exit 1
fi

APN=$1
GPS=${2:-300}

# ensure gps is a number
GPS=$((GPS+0))

hostname=$HOSTNAME
gpsdir=/flash/telemetry/gps

echo "Using APN $APN"
echo "Checking GPS every $GPS seconds"
echo "Starting modem"

qmicli -d /dev/cdc-wdm0 --dms-set-operating-mode='online'
qmicli -d /dev/cdc-wdm0 --dms-get-operating-mode
ip link set wwan0 down
echo 'Y' | tee /sys/class/net/wwan0/qmi/raw_ip
ip link set wwan0 up
qmicli --device=/dev/cdc-wdm0 -p --wds-start-network="ip-type=4,apn=$APN" --client-no-release-cid
udhcpc -i wwan0

if [ $GPS -eq 0 ]; then
    echo "Sleeping..."
    sleep infinity
else

    while true
    do
        mkdir -p $gpsdir
        timestamp=$(date +%s)
        gpsout=$hostname-$timestamp-gps.txt
        echo "Getting GPS"
        echo "Enabling tracking"
        resp=$(qmicli -d /dev/cdc-wdm0 -p --client-no-release-cid --loc-noop)
        arrRESP=(${resp//\'/ })
        cid=${arrRESP[-1]}
        qmicli -d /dev/cdc-wdm0 -p --client-cid="$cid" --client-no-release-cid --loc-start
        qmicli -d /dev/cdc-wdm0 -p --client-cid="$cid" --client-no-release-cid --loc-get-position-report > "$gpsdir/$gpsout"
        echo "Sleeping..."
        sleep $GPS
        qmicli -d /dev/cdc-wdm0 -p --client-cid="$cid" --loc-stop || true
    done
fi
echo "Exiting..."
