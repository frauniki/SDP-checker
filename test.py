import pings
import dns.resolver

v4response = pings.Ping().ping("ipv4.google.com", times=1)
print(vars(v4response))
