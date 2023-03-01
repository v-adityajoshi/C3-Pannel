import time
import atexit
import argparse
import psutil
import datetime
import socket
import getpass
from jtop import jtop, JtopException
from prometheus_client.core import InfoMetricFamily, GaugeMetricFamily, REGISTRY, CounterMetricFamily
from prometheus_client import start_http_server


class CustomCollector(object):
    def __init__(self):
        atexit.register(self.cleanup)
        self._jetson = jtop()
        self._jetson.start()
        self.psutil = psutil

    def cleanup(self):
        print("Closing jetson-stats connection...")
        self._jetson.close()

    def collect(self):
        if self._jetson.ok():
            #
            # Board info
            #
            i = InfoMetricFamily('jetson_info_board', 'Board sys info', labels=['board_info'])
            i.add_metric(['info'], {
                # 'machine': self._jetson.board['info']['machine'],
                # 'jetpack': self._jetson.board['info']['jetpack'],
                # 'l4t': self._jetson.board['info']['L4T'],
                'username': getpass.getuser(),
                'hostname': socket.gethostname()
                })
            yield i

            i = InfoMetricFamily('jetson_info_hardware', 'Board hardware info', labels=['board_hw'])
            i.add_metric(['hardware'], {
                # 'type': self._jetson.board['hardware']['TYPE'],
                # 'codename': self._jetson.board['hardware']['CODENAME'],
                # 'module': self._jetson.board['hardware']['MODULE'],
                # 'board': self._jetson.board['hardware']['BOARD'],
                # 'serial_number': self._jetson.board['hardware']['SERIAL_NUMBER']
                })
            yield i

            #
            # NV power mode
            #
            i = InfoMetricFamily('jetson_nvpmode', 'NV power mode', labels=['nvpmode'])
            i.add_metric(['mode'], {'mode': self._jetson.nvpmodel.name})
            yield i

            #
            # System uptime
            #
            g = GaugeMetricFamily('jetson_uptime', 'System uptime', labels=['uptime'])
            days = self._jetson.uptime.days
            seconds = self._jetson.uptime.seconds
            hours = seconds//3600
            minutes = (seconds//60) % 60
            last_reboot = psutil.boot_time()
            g.add_metric(['days'], days)
            g.add_metric(['hours'], hours)
            g.add_metric(['minutes'], minutes)
            # g.add_metric(['last_reboot'], print(datetime.datetime.fromtimestamp(last_reboot)))
            yield g

            #
            # CPU usage
            #
            # g = GaugeMetricFamily('jetson_usage_cpu', 'CPU % schedutil', labels=['cpu'])
            # g.add_metric(['cpu_1'], self._jetson.cpu['CPU1']['val'])
            # g.add_metric(['cpu_2'], self._jetson.cpu['CPU2']['val'])
            # g.add_metric(['cpu_3'], self._jetson.cpu['CPU3']['val'])
            # g.add_metric(['cpu_4'], self._jetson.cpu['CPU4']['val'])
            # g.add_metric(['cpu_5'], self._jetson.cpu['CPU5']['val'])
            # g.add_metric(['cpu_6'], self._jetson.cpu['CPU6']['val'])
            #g.add_metric(['cpu_7'], self._jetson.cpu['CPU7']['val'])
            #g.add_metric(['cpu_8'], self._jetson.cpu['CPU8']['val'])
            # yield g

            #
            # GPU usage
            #
            # g = GaugeMetricFamily('jetson_usage_gpu', 'GPU % schedutil', labels=['gpu'])
            # g.add_metric(['val'], self._jetson.gpu['val'])
            # g.add_metric(['frq'], self._jetson.gpu['frq'])
            # g.add_metric(['min_freq'], self._jetson.gpu['min_freq'])
            # g.add_metric(['max_freq'], self._jetson.gpu['max_freq'])
            # yield g

            #
            # RAM usage
            #
            # g = GaugeMetricFamily('jetson_usage_ram', 'Memory usage', labels=['ram'])
            # g.add_metric(['used'], self._jetson.ram['use'])
            # g.add_metric(['shared'], self._jetson.ram['shared'])
            # g.add_metric(['total'], self._jetson.ram['tot'])
            # g.add_metric(['unit'], self._jetson.ram['unit'])
            # yield g

            #
            # Disk usage
            #
            g = GaugeMetricFamily('jetson_usage_disk', 'Disk space usage', labels=['disk'])
            g.add_metric(['free'], self.psutil.disk_usage("/data").free /10**9)
            g.add_metric(['total'], self.psutil.disk_usage("/data").total /10**9)
            g.add_metric(['used'], self.psutil.disk_usage("/data").used /10**9)
            g.add_metric(['percent'], self.psutil.disk_usage("/data").percent)
            yield g

            # g = GaugeMetricFamily('jetson_usage_rootdisk', 'Disk space usage-root', labels=['root'])
            # g.add_metric(['used'], self._jetson.disk['used'])
            # yield g


            #
            # Fan usage
            #
            g = GaugeMetricFamily('jetson_usage_fan', 'Fan usage', labels=['fan'])
            g.add_metric(['speed'], self._jetson.fan['speed'])
            yield g

            #
            # Sensor temperatures
            #
            g = GaugeMetricFamily('jetson_temperatures', 'Sensor temperatures', labels=['temperature'])
            g.add_metric(['gpu'], self._jetson.temperature['GPU'] if 'GPU' in self._jetson.temperature else 0)
            g.add_metric(['thermal'], self._jetson.temperature['thermal'] if 'thermal' in self._jetson.temperature else 0)
            yield g

            #
            # Power
            #
            g = GaugeMetricFamily('jetson_usage_power', 'Power usage', labels=['power'])
            g.add_metric(['soc'], self._jetson.power[1]['SOC']['cur'] if 'SOC' in self._jetson.power[1] else 0)
            yield g


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=9000, help='Metrics collector port number')

    args = parser.parse_args()

    start_http_server(args.port)
    REGISTRY.register(CustomCollector())
    while True:
        time.sleep(1)
