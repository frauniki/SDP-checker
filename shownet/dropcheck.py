import pings
import requests
import netifaces
import iptools
from dns import resolver
from pyfiglet import Figlet

from shownet.function_check import traceroute
from shownet.response import Response, ping_append_method


class DropCheck:
    nic_name = None
    v4target = None
    v6target = None
    ping_test_count = 2
    function = {}
    console_out = False
    debug = False

    def __init__(self):
        self.response = Response()

        if self.function:
            self.function_index = {}
            for func in self.function:
                for func_ip in self.function[func]['ip']:
                    self.function_index[func_ip] = func

    def all_check(self):
        self.aa_title()
        self.ip()
        self.ping()
        self.dns()
        self.service()
        self.http()
        self._console_out("* Complite!")

    def aa_title(self):
        f = Figlet(font="slant")
        msg = f.renderText("ShowNet DropCheck")
        self._console_out(msg)

    def _console_out(self, msg, head=False):
        if self.console_out:
            if head:
                msg = f"#### {msg}"
            print(msg)

    def ip(self):
        self._console_out(
            f"Starting: IP Check\nInterface = {self.nic_name}\n", True)
        result = netifaces.ifaddresses(self.nic_name)

        try:
            self.response.ip_v4.address = result[netifaces.AF_INET][0]['addr']
            self.response.ip_v4.prefix = str(iptools.ipv4.netmask2prefix(
                result[netifaces.AF_INET][0]['netmask']))
        except Exception as err:
            self.response.ip_v4.address = ""
            self.response.ip_v4.prefix = ""
        try:
            self.response.ip_v6.address = result[netifaces.AF_INET6][1]['addr']
            self.response.ip_v6.prefix = str(result[netifaces.AF_INET6][1]['netmask'].split(
                "/")[1])
        except Exception as err:
            self.response.ip_v6.address = ""
            self.response.ip_v6.prefix = ""

        if self.console_out:
            self.response.ip_v4.table_console_out()
            self.response.ip_v6.table_console_out()

    def ping(self):
        self._console_out(
            f"Starting: Ping Check\nIPv4 Target Host = {self.v4target}\nIPv6 Target Host = {self.v6target}\n", True)
        self.response.ping_v4 = pings.Ping(quiet=(not self.debug)).ping(
            self.v4target, times=self.ping_test_count)
        self.response.ping_v6 = pings.Ping().ping(
            self.v6target, times=self.ping_test_count)

        ping_append_method(self.response.ping_v4)
        ping_append_method(self.response.ping_v6)

        if self.console_out:
            self.response.ping_v4.table_console_out()
            self.response.ping_v6.table_console_out()

    def dns(self):
        self._console_out(
            f"Starting: DNS Check\nA Record = {self.v4target}\nAAAA Record = {self.v6target}\n", True)
        try:
            a = resolver.query(self.v4target, "A")
            self.response.dns_a.record_name = str(a.qname)
            self.response.dns_a.data = str([x for x in a][0])
        except Exception as err:
            print(f"dns check error -> {err}")
        try:
            aaaa = resolver.query(self.v6target, "AAAA")
            self.response.dns_aaaa.record_name = str(aaaa.qname)
            self.response.dns_aaaa.data = str([x for x in aaaa][0])
        except Exception as err:
            print(f"dns check error -> {err}")

        if self.console_out:
            self.response.dns_a.table_console_out()
            self.response.dns_aaaa.table_console_out()

    def service(self):
        self._console_out(
            f"Starting: Service Chain Check\nIPv4 Target Host = {self.v4target}\nIPv6 Target Host = {self.v6target}\n", True)
        try:
            self.response.service_v4.data = self.function_replace(
                traceroute(self.v4target))
        except Exception as err:
            print(f"service check error -> {err}")
        try:
            self.response.service_v6.data = self.function_replace(
                traceroute(self.v6target))
        except Exception as err:
            print(f"service check error -> {err}")

        if self.console_out:
            self.response.service_v4.table_console_out()
            self.response.service_v6.table_console_out()

    def function_replace(self, data):
        for i in data:
            if i[1] in self.function_index:
                i[1] = self.function_index[i[1]]

        return data

    def http(self):
        self._console_out(
            f"Starting: HTTP Check\nIPv4 Target Host = http://{self.v4target}\nIPv6 Target Host = http://{self.v6target}\n", True)
        self.response.http_v4.dest = f"https://{self.v4target}/"
        self.response.http_v6.dest = f"https://{self.v6target}/"
        try:
            v4response = requests.get(self.response.http_v4.dest)
            self.response.http_v4.status_code = v4response.status_code
        except Exception as err:
            print(f"http check error -> {err}")
        try:
            v6response = requests.get(self.response.http_v6.dest)
            self.response.http_v6.status_code = v6response.status_code
        except Exception as err:
            print(f"http check error -> {err}")

        if self.console_out:
            self.response.http_v4.table_console_out()
            self.response.http_v6.table_console_out()
