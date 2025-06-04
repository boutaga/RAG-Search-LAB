import os
import time
import psutil
from prometheus_client import start_http_server, Gauge, Counter

REQUEST_COUNT = Counter('raglab_requests_total', 'Total requests processed')
CPU_GAUGE = Gauge('raglab_cpu_percent', 'CPU usage percent')
MEMORY_GAUGE = Gauge('raglab_memory_percent', 'Memory usage percent')


def collect_metrics():
    CPU_GAUGE.set(psutil.cpu_percent(interval=None))
    MEMORY_GAUGE.set(psutil.virtual_memory().percent)


def main():
    host = os.getenv('METRICS_EXPORTER_HOST', '0.0.0.0')
    port = int(os.getenv('METRICS_EXPORTER_PORT', '9100'))
    start_http_server(port, addr=host)
    while True:
        collect_metrics()
        time.sleep(5)


if __name__ == '__main__':
    main()
