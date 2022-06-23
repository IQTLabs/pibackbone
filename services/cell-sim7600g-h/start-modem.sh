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
gpstempfile=/var/tmp/gpstime

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
ip link set dev wwan0 mtu 900

function get_loc()
{
    #maximum number of attempts to get a satellite fix before defaulting to cellular
    max_attempts=5
    #time between attempts to get a satellite fix
    time_between_attempts=30
    satellite_connection_flag=0

    gps_dir=${1}
    gps_out=${2}

    echo "Getting GPS"
    echo "Enabling tracking"

    #get cid
    resp=$(qmicli -d /dev/cdc-wdm0 -p --client-no-release-cid --loc-noop)
    arrRESP=(${resp//\'/ })
    cid=${arrRESP[-1]}

    #start location tracking and wait a bit for it to lock
    qmicli -d/dev/cdc-wdm0 -p --client-cid="$cid" --client-no-release-cid --loc-start
    sleep 35 

    #while we haven't reached our maximum attempts and while we haven't established a satellite lock
    while [ $max_attempts -gt 0 ] && [ $satellite_connection_flag -ne 1 ]
    do
        #get our position report
        posreport=$(qmicli -d /dev/cdc-wdm0 -p --client-cid="$cid" --client-no-release-cid --loc-get-position-report)
        
        #check if our position report is based on a satellite lock or if we're on our last attempt
        if [[ $posreport == *"technology: satellite"* ]] || [[ $max_attempts -eq 1 ]]; then
            #if satellite lock is acquired, write the gps info, stop location tracking, and set our satellite connection 
            #flag to true
            echo $posreport > "$gpsdir/$gpsout"
            qmicli -d /dev/cdc-wdm0 -p --client-cid="$cid" --loc-stop || true
            satellite_connection_flag=1
        else
            #reduce our max attempts and try again in a few
            ((max_attempts -= 1))
            sleep $time_between_attempts
        fi
    done

}

if [ $GPS -eq 0 ]; then
    echo "Sleeping..."
    sleep infinity
else
    while true
    do
        currentepochtime=$(date +%s)
        #if our persistent time temp file exists
        if [ -f $gpstempfile ]; then
            goaltime=$(cat $gpstempfile)
            #see if our current time is greater than or equal to the previous goaltime
            if [ $currentepochtime -ge $goaltime ]; then
                mkdir -p $gpsdir
                timestamp=$(date +%s)
                gpsout=$hostname-$timestamp-gps.txt
                get_loc "$gpsdir" "$gpsout"
                #update the next goaltime we need to get loc
                echo $((currentepochtime+GPS)) > $gpstempfile
                echo "Sleeping..."
                sleep $GPS
            fi
        else
                mkdir -p $gpsdir
                timestamp=$(date +%s)
                gpsout=$hostname-$timestamp-gps.txt
                get_loc "$gpsdir" "$gpsout"
                #update the next goaltime we need to get loc
                echo $((currentepochtime+GPS)) > $gpstempfile
                echo "Sleeping..."
                sleep $GPS
        fi
    done
fi
echo "Exiting..."
