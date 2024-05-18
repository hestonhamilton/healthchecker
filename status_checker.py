#!/usr/bin/env python3
from prometheus_client import start_http_server, Gauge
import requests
import time
import asyncio
from kasa import SmartStrip

# Configuration
CHECK_INTERVAL = 60  # 1 minute
URL = "https://birdnetaz.com/"
PLUG_IP = "192.168.0.62"  # Replace with your smart strip IP
PLUG_NAME = "Plug 5"  # Replace with your smart strip port name

# Prometheus metric
status_code_gauge = Gauge('website_status_code', 'HTTP status code of the website')

# Function to check website status and toggle smart switch if necessary
async def check_website_status():
    try:
        response = requests.get(URL)
        status_code = response.status_code
        status_code_gauge.set(status_code)

        if 500 <= status_code < 600:
            print(f"Bad status code {status_code}. Toggling the smart switch.")
            strip = SmartStrip(PLUG_IP)
            await strip.update()
            for plug in strip.children:
                if plug.alias == PLUG_NAME:
                    await plug.turn_off()
                    time.sleep(5)
                    await plug.turn_on()
                    break
    except Exception as e:
        print(f"Error checking website status: {e}")
        status_code_gauge.set(0)

if __name__ == '__main__':
    start_http_server(8000)
    loop = asyncio.get_event_loop()
    while True:
        loop.run_until_complete(check_website_status())
        time.sleep(CHECK_INTERVAL)

