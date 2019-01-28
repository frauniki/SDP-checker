import json
import copy
import netifaces
import iptools
import pings
import dns.resolver
from operator import itemgetter
from lib.function_check import traceroute


class check():
    def __init__(self, nic_name, functions, exhibitor_service_chain):
        self.nic_name = nic_name
        self.ip = ip_check(nic_name)
        self.ping = ping_check(test_count=1)
        self.dns = dns_check()
        self.functions = functions
        self.exhibitor_service_chain = exhibitor_service_chain
        self.service_chain = service_chain(
            all_functions_data=self.functions, exhibitor_service_chain=self.exhibitor_service_chain["akina"])


class ip_check():
    def __init__(self, nic_name: str, ipv4_addr="0.0.0.0", ipv4_prefix=32, v4status=False, ipv6_addr="::", ipv6_prefix=128, v6status=False):
        self.ipv4_addr = ipv4_addr
        self.ipv4_prefix = ipv4_prefix
        self.v4status = v4status
        self.ipv6_addr = ipv6_addr
        self.ipv6_prefix = ipv6_prefix
        self.v6status = v6status
        self._test(nic_name)

    def _test(self, nic_name: str) -> None:
        result = netifaces.ifaddresses(nic_name)
        self.ipv4_addr = result[netifaces.AF_INET][0]['addr']
        self.ipv4_prefix = iptools.ipv4.netmask2prefix(
            result[netifaces.AF_INET][0]['netmask'])
        try:
            self.ipv6_addr = result[netifaces.AF_INET6][1]['addr']
            self.ipv6_prefix = result[netifaces.AF_INET6][1]['netmask'].split(
                "/")[1]
        except:
            self.ipv6_addr = None
            self.ipv6_prefix = None
        self._check()

    def _check(self) -> None:
        # debug
        self.v4status = True
        self.v6status = True


class ping_check():
    def __init__(self, v4target="ipv4.google.com", v4status=False, v6target="ipv6.google.com", v6status=False, test_count=1):
        self.test_count = test_count
        self.v4target = v4target
        self.v4response = None
        self.v4status = v4status
        self.v6target = v6target
        self.v6response = None
        self.v6status = v6status
        self._test()

    def _test(self) -> None:
        v4result = pings.Ping().ping(self.v4target, times=self.test_count)
        self.v4response = v4result
        self.v4status = v4result.is_reached()
        v6result = pings.Ping().ping(self.v6target)
        self.v6response = v6result
        self.v6status = v6result.is_reached()


class dns_check():
    def __init__(self, v4target="ipv4.google.com", v4status=False, v6target="ipv6.google.com", v6status=False):
        self.v4target = v4target
        self.v4response = None
        self.v4status = v4status
        self.v6target = v6target
        self.v6response = None
        self.v6status = v6status
        self._test()

    def _test(self) -> None:
        try:
            v4result = dns.resolver.query(self.v4target, "A")
            self.v4response = [i for i in v4result]
            self.v4status = True
        except Exception as err:
            self.v4response = [err]
            self.v4status = False
        try:
            v6result = dns.resolver.query(self.v6target, "AAAA")
            self.v6response = [i for i in v6result]
            self.v6status = True
        except Exception as err:
            self.v6response = [err]
            self.v4status = False


class function():
    def __init__(self, function_pool=None, function_name=None, function_type=None, included_address=None):
        self.function_pool = function_pool
        self.function_name = function_name
        self.function_type = function_type
        self.included_address = included_address
        self.order = 0
        self.order_check = False


class service_chain():
    def __init__(self, v4target="ipv4.google.com", v4status=False, v6target="ipv6.google.com", v6status=False, all_functions_data=None, exhibitor_service_chain=None):
        self.v4target = v4target
        self.v4status = v4status
        self.v4response = None
        self.v6target = v6target
        self.v6status = v6status
        self.v6response = None
        self.all_functions_data = all_functions_data
        self.exhibitor_service_chain = exhibitor_service_chain
        if self.all_functions_data != None and self.exhibitor_service_chain != None:
            self._test()

    def _test(self) -> None:
        try:
            v4result = traceroute(self.v4target)
            self.v4status, self.v4response = self._function_decision(v4result)
        except Exception as err:
            self.v4status = False
        try:
            v6result = traceroute(self.v6target)
            self.v6status, self.v6response = self._function_decision(v6result)
        except:
            self.v6response = [function()]
            self.v6status = False

    def _function_decision(self, req_data):
        index = {}
        response = []
        function_num = 1
        for function_pool in self.all_functions_data:
            for function_data in self.all_functions_data[function_pool]:
                for ip in self.all_functions_data[function_pool][function_data]["included_address"]:
                    index[ip] = function(function_pool, function_data, self.all_functions_data[function_pool][function_data]["function_type"],
                                         self.all_functions_data[function_pool][function_data]["included_address"])
        for i in req_data:
            ip = i[1]
            if ip in index:
                service_function = copy.copy(index[ip])
                service_function.order = function_num
                response.append(service_function)
                function_num += 1
        self.exhibitor_service_chain.sort(key=itemgetter(0))
        status = True
        for i in response:
            exhibitor_service = self.exhibitor_service_chain[i.order - 1]
            if i.order == exhibitor_service[0] and i.function_name == exhibitor_service[1]:
                i.order_check = True
            else:
                i.order_check = False
                status = False
        return status, response


def to_dict(data):
    return {
        "ip": {
            "v4": {
                "address": data.ip.ipv4_addr,
                "prefix": data.ip.ipv4_prefix,
                "status": data.ip.v4status
            },
            "v6": {
                "address": data.ip.ipv6_addr,
                "prefix": data.ip.ipv6_prefix,
                "status": data.ip.v6status
            }
        },
        "ping": {
            "v4": {
                "response": vars(data.ping.v4response),
                "status": data.ping.v4status
            },
            "v6": {
                "response": vars(data.ping.v6response),
                "status": data.ping.v6status
            }
        },
        "dns": {
            "A": {
                "response": [str(i) for i in data.dns.v4response],
                "status": data.dns.v4status
            },
            "AAAA": {
                "response": [str(i) for i in data.dns.v6response],
                "status": data.dns.v6status
            }
        },
        "service_chain": {
            "v4": {
                "response": [vars(i) for i in data.service_chain.v4response],
                "status": data.service_chain.v4status
            },
            "v6": {
                "response": [vars(i) for i in data.service_chain.v6response],
                "status": data.service_chain.v6status
            }
        }
    }


def to_json(data, indent=None):
    return json.dumps(to_dict(data), indent=indent)
