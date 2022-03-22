import glob
import json
import os
import socket
import subprocess
import time

import docker

from hooks import insert_message_data
from hooks import send_hook


class Telemetry:

    def __init__(self, base_dir='/flash/telemetry'):
        # plus 0.5 second for status per wake and plus time to run loop
        self.MINUTES_BETWEEN_WAKES = 0.1  # roughly every 5 seconds (not 6 because of the above considerations)
        self.MINUTES_BETWEEN_WRITES = 15
        self.CYCLES_BEFORE_STATUS_CHECK = 1/self.MINUTES_BETWEEN_WAKES
        # if waking up less than once a minute, just set the status check to the same amount of time as the wake cycle
        if self.CYCLES_BEFORE_STATUS_CHECK < 1:
            self.CYCLES_BEFORE_STATUS_CHECK = self.MINUTES_BETWEEN_WAKES

        self.hostname = os.getenv("HOSTNAME", socket.gethostname())
        self.location = os.getenv("LOCATION", "unknown")
        self.version = os.getenv("VERSION", "")
        self.sensor_dir = os.path.join(base_dir, 'sensors')
        self.sensor_data = None
        self.alerts = {}
        self.docker = docker.from_env()

    @staticmethod
    def check_internet():
        try:
            output = subprocess.check_output("/internet_check.sh")
        except Exception as e:
            print(f'Failed to check internet because: {e}')
            output = b'Failed'

        if b'Online' in output:
            return True
        return False

    def get_container_version(self, container):
        env_vars = container.attrs['Config']['Env']
        for env_var in env_vars:
            if env_var.startswith("VERSION="):
                return env_var.split("=")[-1]
        return ""

    def init_sensor_data(self):
        self.sensor_data = {"system_load": [],
                            "memory_used_mb": [],
                            "internet": [],
                            "disk_free_gb": [],
                            "uptime_seconds": [],
                            "version_sense": [],
                           }

    def write_sensor_data(self, timestamp):
        status = self.status_hook()
        print(f'Status update response: {status}')

    def shutdown_hook(self, subtitle):
        data = {}
        data['title'] = os.path.join(self.hostname, self.location)
        data['themeColor'] = "d95f02"
        data['body_title'] = "Shutting system down"
        data['body_subtitle'] = subtitle
        data['text'] = ""
        data['facts'] = self.status_data()
        card = insert_message_data(data)
        status = send_hook(card)
        return status

    def status_hook(self):
        checks = len(self.alerts)
        health = 0
        unhealthy = []
        for alert in self.alerts:
            if self.alerts[alert]:
                unhealthy.append(alert)
            else:
                health += 1

        data = {}
        data['title'] = os.path.join(self.hostname, self.location)
        data['body_title'] = "Status Update"
        data['body_subtitle'] = f'{health} / {checks} checks healthy'
        if health < checks:
            data['themeColor'] = "d95f02"
        data['text'] = f'Checks that alerted: {unhealthy}'
        data['facts'] = self.status_data()
        card = insert_message_data(data)
        status = send_hook(card)
        return status

    def status_data(self):
        facts = []
        for key in self.sensor_data.keys():
            if len(self.sensor_data[key]) > 0:
                facts.append({"name": key, "value": str(self.sensor_data[key][-1][0])})
        return facts

    def run_checks(self, timestamp):
        # internet: check if available
        inet = self.check_internet()
        self.sensor_data["internet"].append([inet, timestamp])
        if inet:
            self.alerts['internet'] = False
        else:
            self.alerts['internet'] = True

        # system health: load
        load = os.getloadavg()
        self.sensor_data["system_load"].append([load[0], timestamp])
        if load[0] > 2:
            self.alerts['system_load'] = True
        elif load[0] > 1:
            self.alerts['system_load'] = False
        else:
            self.alerts['system_load'] = False

        # system health: memory
        total_memory, used_memory, free_memory = map(int, os.popen('free -t -m').readlines()[1].split()[1:4])
        self.sensor_data["memory_used_mb"].append([used_memory, timestamp])
        if used_memory/total_memory > 0.9:
            self.alerts['memory_used_mb'] = True
        elif used_memory/total_memory > 0.7:
            self.alerts['memory_used_mb'] = False
        else:
            self.alerts['memory_used_mb'] = False

        # system health: disk space
        st = os.statvfs('/')
        bytes_avail = (st.f_bavail * st.f_frsize)
        gb_free = round(bytes_avail / 1024 / 1024 / 1024, 1)
        self.sensor_data["disk_free_gb"].append([gb_free, timestamp])
        if gb_free < 2:
            self.alerts['disk_free_gb'] = True
        elif gb_free < 10:
            self.alerts['disk_free_gb'] = False
        else:
            self.alerts['disk_free_gb'] = False

        # system uptime (linux only!)
        self.sensor_data["uptime_seconds"].append([time.clock_gettime(time.CLOCK_BOOTTIME), timestamp])


    def main(self, run_forever):
        os.makedirs(self.sensor_dir, exist_ok=True)
        self.init_sensor_data()

        # Cycle through getting readings forever
        cycles = 1
        write_cycles = 1
        running = True
        while running:
            running = run_forever

            # TODO: write out data if exception with a try/except
            timestamp = int(time.time()*1000)

            # Check if a shutdown has been signaled
            signal_contents = ""
            try:
                with open('/var/run/shutdown.signal', 'r') as f:
                    signal_contents = f.read()
            except Exception as e:
                pass

            if signal_contents.strip() == 'true':
                self.shutdown_hook("Low battery")

            if cycles == self.CYCLES_BEFORE_STATUS_CHECK or self.MINUTES_BETWEEN_WAKES > 1:
                self.run_checks(timestamp)
                cycles = 1
                write_cycles += 1

            # Write out data
            if write_cycles == self.MINUTES_BETWEEN_WRITES:
                write_timestamp = int(time.time())
                self.write_sensor_data(write_timestamp)
                self.init_sensor_data()
                write_cycles = 1

            # Sleep between cycles
            time.sleep(60*self.MINUTES_BETWEEN_WAKES)

            cycles += 1


if __name__ == '__main__':
    t = Telemetry()
    t.main(True)
