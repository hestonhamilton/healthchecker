#!/usr/bin/env python3
import requests
import time
import asyncio
import os
from prometheus_client import start_http_server, Gauge
from kasa import SmartStrip

# Configuration
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 60))  # 1 minute by default
HOSTS = [
    {
        "name": "birdnetaz",
        "url": "https://birdnetaz.com/",
        "action": "toggle_plug",
        "plug_ip": "192.168.0.62",
        "plug_name": "Plug 5"
    },
    {
        "name": "plex",
        "url": "https://thegingeraffe.com/",
        "action": "log_status"
    }
    # Add more hosts here with their specific actions
]

# Prometheus metrics
status_code_gauges = {}

def initialize_metrics():
    """Initialize Prometheus metrics for each host."""
    for host in HOSTS:
        url = host['url']
        gauge_name = f"website_status_code_{host['name']}"
        status_code_gauges[host['name']] = Gauge(gauge_name, f'HTTP status code of the website {url}')

def get_status_code(url):
    """Get the HTTP status code of a website."""
    try:
        response = requests.get(url)
        return response.status_code
    except requests.RequestException as e:
        print(f"Error checking website status for {url}: {e}")
        return 0

async def toggle_plug(plug_ip, plug_name):
    """Toggle a specific plug on a smart strip."""
    try:
        strip = SmartStrip(plug_ip)
        await strip.update()
        for plug in strip.children:
            if plug.alias == plug_name:
                await plug.turn_off()
                time.sleep(5)
                await plug.turn_on()
                break
    except Exception as e:
        print(f"Error toggling plug {plug_name} on {plug_ip}: {e}")

async def perform_action(host, status_code):
    """Perform an action based on the host configuration and status code."""
    action = host.get('action')

    if action == "toggle_plug" and 400 <= status_code < 600:
        print(f"Bad status code {status_code} for {host['url']}. Toggling the smart switch.")
        await toggle_plug(host['plug_ip'], host['plug_name'])
    elif action == "log_status":
        print(f"Status code for {host['url']}: {status_code}")
    # Add more actions here as needed

async def check_host(host):
    """Check the status of a host and perform the configured action."""
    status_code = get_status_code(host['url'])
    status_code_gauges[host['name']].set(status_code)
    await perform_action(host, status_code)

async def main():
    """Main loop to continuously check the status of each configured host."""
    while True:
        tasks = [check_host(host) for host in HOSTS]
        await asyncio.gather(*tasks)
        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    start_http_server(8000)
    initialize_metrics()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())