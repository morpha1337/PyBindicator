"""Wi-Fi connection, NTP time sync, and HTTP helpers."""

from __future__ import annotations

import wifi
import rtc
import adafruit_ntp
import adafruit_requests
import ssl
import socketpool
import json
from time import struct_time
from helpers import format_struct_time


class WifiController:
    """Connect to the AP and fetch network resources."""

    ssid: str
    password: str
    retries: int
    timeout: int

    def __init__(self, secrets: dict, config: dict) -> None:
        self.ssid = secrets["ssid"]
        self.password = secrets["password"]
        self.retries = config["retries"]
        self.timeout = config["timeout"]

        if not self.ssid or not self.password:
            raise Exception("WiFi secrets are kept in secrets.py, please add them there!")

    def scan_network(self) -> None:
        print("Available WiFi networks:")
        for network in wifi.radio.start_scanning_networks():
            print(
                "\t%s\t\trssi: %d\tchannel: %d"
                % (str(network.ssid, "utf-8"), network.rssi, network.channel)
            )
        wifi.radio.stop_scanning_networks()
        print("======================")

    def connect(self) -> None:
        """Join the configured AP, retrying up to self.retries times."""
        tries = 1
        connected = False
        print("Connecting to WIFI: %s" % self.ssid)
        while not connected and tries <= self.retries:
            try:
                wifi.radio.connect(self.ssid, self.password, timeout=self.timeout)
                connected = True
            except ConnectionError as e:
                print("[ERROR] could not connect to AP, retrying: ", e, ", Attempts: ", tries)
                tries += 1
                continue

        assert connected, "Failed to connect to Wifi with SSID: %s" % self.ssid
        print("Connected! My IP address is: ", wifi.radio.ipv4_address)

    def set_date_time(self, timezone_offset: int) -> struct_time:
        """Sync RTC from NTP using the given hours-from-UTC offset."""
        tries = 1
        success = False
        ntp = None
        while not success and tries <= self.retries:
            try:
                pool = socketpool.SocketPool(wifi.radio)
                ntp = adafruit_ntp.NTP(pool, tz_offset=timezone_offset)
                rtc.RTC().datetime = ntp.datetime
                success = True
            except OSError as e:
                print("[ERROR] could not get time, retrying: ", e, ", Attempts: ", tries)
                tries += 1
                continue

        print("The current Date Time is: ", format_struct_time(ntp.datetime))
        return ntp.datetime

    def print_network_info(self) -> None:
        print("==============")
        print("My MAC address:", [hex(i) for i in wifi.radio.mac_address])
        print("My IP address: ", wifi.radio.ipv4_address)
        print("==============")

    def call_url(self, url: str) -> str:
        pool = socketpool.SocketPool(wifi.radio)
        requests = adafruit_requests.Session(pool, ssl.create_default_context())

        print("Calling URL: ", url)
        response = requests.get(url)
        result = response.text
        response.close()
        return result

    def call_url_json(self, url: str) -> dict:
        pool = socketpool.SocketPool(wifi.radio)
        requests = adafruit_requests.Session(pool, ssl.create_default_context())

        print("Calling URL: ", url)
        response = requests.get(url)
        result = response.json()
        response.close()
        return result

    def ping(self, ipaddress: str) -> None:
        ipv4 = ipaddress.ip_address(ipaddress)
        pingres = wifi.radio.ping(ipv4) * 1000
        if pingres > 0:
            print("internet connectivity is up")
            print("ping google.com: %f ms" % pingres)
        else:
            print("no internet connection or google is down?")

    def test_wifi(self) -> None:
        joke = self.call_url("https://api.chucknorris.io/jokes/random")
        print(json.loads(joke)["value"])
