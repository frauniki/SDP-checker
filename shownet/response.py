import json
import types
import pings
import prettytable


class Table(object):
    def __init__(self, header=["Key", "Value"]):
        self.header = header

    def _to_table(self):
        return []

    def table_console_out(self):
        if self._to_table():
            table = prettytable.PrettyTable(self.header)
            for other in self._to_table():
                table.add_row(other)
            print(table)


class Ip(Table):
    def __init__(self):
        super().__init__()

        self.address = None
        self.prefix = None
        self.gateway = None

    def _to_table(self):
        return [
            ["CIDR", self.to_cider()]
        ]

    def to_dict(self):
        return {
            "cidr": self.to_cider(),
            "address": self.address,
            "prefix": self.prefix,
            "gateway": self.gateway
        }

    def to_cider(self):
        return f"{self.address}/{str(self.prefix)}"


class Dns(Table):
    def __init__(self):
        super().__init__()

        self.record_name = None
        self.data = None

    def _to_table(self):
        return [
            ["Record Name", self.record_name],
            ["Data", self.data]
        ]

    def to_dict(self):
        return {
            "record_name": self.record_name,
            "data": self.data
        }


class Service(Table):
    def __init__(self):
        super().__init__(header=["Hop", "HostName", "HostIP"])

        self.data = None

    def _to_table(self):
        return self.data

    def to_dict(self):
        return {
            "data": self.data
        }


class Http(Table):
    def __init__(self):
        super().__init__()

        self.dest = None
        self.status_code = None

    def _to_table(self):
        return [
            ["Dest", self.dest],
            ["Status Code", self.status_code]
        ]

    def to_dict(self):
        return {
            "dest": self.dest,
            "status_code": self.status_code
        }


class Response(object):
    def __init__(self):
        self.ip_v4 = Ip()
        self.ip_v6 = Ip()
        self.ping_v4 = pings.Response()
        self.ping_v6 = pings.Response()
        self.dns_a = Dns()
        self.dns_aaaa = Dns()
        self.service_v4 = Service()
        self.service_v6 = Service()
        self.http_v4 = Http()
        self.http_v6 = Http()

    def __str__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {
            "ip": {
                "v4": self.ip_v4.to_dict(),
                "v6": self.ip_v6.to_dict()
            },
            "ping": {
                "v4": self.ping_v4.to_dict(),
                "v6": self.ping_v6.to_dict()
            },
            "dns": {
                "a": self.dns_a.to_dict(),
                "aaaa": self.dns_aaaa.to_dict()
            },
            "service": {
                "v4": self.service_v4.to_dict(),
                "v6": self.service_v6.to_dict()
            },
            "http": {
                "v4": self.http_v4.to_dict(),
                "v6": self.http_v6.to_dict()
            }
        }

    def to_json(self, indent=None):
        return json.dumps(self.to_dict(), indent=indent)


def ping_append_method(instance):
    def _to_table(self):
        return [
            ["Max RTT", self.max_rtt],
            ["Min RTT", self.min_rtt],
            ["Avg RTT", self.avg_rtt],
            ["Packet Lost", self.packet_lost],
            ["Packet Size", self.packet_size],
            ["Timeout", self.timeout],
            ["Dest", self.dest],
            ["Dest IP", self.dest_ip]
        ]

    instance.header = ["Key", "Value"]
    instance.table_console_out = types.MethodType(
        Table.table_console_out, instance)
    instance._to_table = types.MethodType(_to_table, instance)
