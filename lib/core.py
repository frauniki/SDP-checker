import json
import netifaces
import iptools
import pings
import dns.resolver


class check():
    def __init__(self, nic_name):
        self.nic_name = nic_name
        self.ip = ip_check(nic_name)
        self.ping = ping_check(test_count=1)
        self.dns = dns_check()
        self.service_chain = service_chain()


class ip_check():
    def __init__(self, nic_name, ipv4_addr="0.0.0.0", ipv4_prefix=32, v4status=False, ipv6_addr="::", ipv6_prefix=128, v6status=False):
        self.ipv4_addr = ipv4_addr
        self.ipv4_prefix = ipv4_prefix
        self.v4status = v4status
        self.ipv6_addr = ipv6_addr
        self.ipv6_prefix = ipv6_prefix
        self.v6status = v6status
        self._test(nic_name)

    def _test(self, nic_name):
        result = netifaces.ifaddresses(nic_name)
        self.ipv4_addr = result[netifaces.AF_INET][0]['addr']
        self.ipv4_prefix = iptools.ipv4.netmask2prefix(
            result[netifaces.AF_INET][0]['netmask'])
        self.ipv6_addr = result[netifaces.AF_INET6][1]['addr']
        self.ipv6_prefix = result[netifaces.AF_INET6][1]['netmask'].split(
            "/")[1]
        self._check()

    def _check(self):
        # debug
        self.v4status = True
        self.v6status = True


class ping_check():
    def __init__(self, v4target="ipv4.google.com", v4status=False, v6target="ipv6.google.com", v6status=False, test_count=1):
        self.test_count = test_count
        self.v4target = v4target
        self.v4response = None
        self.v4status = v4status
        self.v6target = v4target
        self.v6response = None
        self.v6status = v4status
        self._test()

    def _test(self):
        self.v4response = pings.Ping().ping(self.v4target, times=self.test_count)
        self.v4status = self.v4response.is_reached()
        print(self.v4status)
        self.v6response = pings.Ping().ping(self.v6target)
        self.v6status = self.v6response.is_reached()


class dns_check():
    def __init__(self, v4target="ipv4.google.com", v4status=False, v6target="ipv6.google.com", v6status=False):
        self.v4target = v4target
        self.v4response = None
        self.v4status = v4status
        self.v6target = v6target
        self.v6response = None
        self.v6status = v6status
        self._test()

    def _test(self):
        try:
            self.v4response = dns.resolver.query(self.v4target, "A")
            self.v4status = True
        except Exception as err:
            self.v4response = err
        try:
            self.v6response = dns.resolver.query(self.v6target, "AAAA")
            self.v6status = True
        except Exception as err:
            self.v6response = err


class service_chain():
    def __init__(self, v4status=False, v6status=False):
        self.v4status = v4status
        self.v6status = v6status

    def _test(self):
        pass


def to_dict(data):
    return {
        "ip": {
            "ipv4_addr": data.ip.ipv4_addr,
            "ipv4_prefix": data.ip.ipv4_prefix,
            "v4status": data.ip.v4status,
            "ipv6_addr": data.ip.ipv6_addr,
            "ipv6_prefix": data.ip.ipv6_prefix,
            "v6status": data.ip.v6status
        },
        "ping": {
            "v4status": data.ping.v4status,
            "v6status": data.ping.v6status
        },
        "dns": {
            "v4status": data.dns.v4status,
            "v6status": data.dns.v6status
        },
        "service_chain": {
            "v4status": False,
            "v6status": False
        }
    }


def to_json(data, indent=None):
    return json.dumps(to_dict(data), indent=indent)
