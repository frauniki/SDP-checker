import sys
import socket


def traceroute(dest_name, max_hops=30):
    dest_addr = socket.gethostbyname(dest_name)

    socket.setdefaulttimeout(1)
    icmp = socket.getprotobyname('icmp')
    ttl = 1
    response = []

    while True:
        recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, icmp)
        send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
        recv_socket.bind(("", 0))
        send_socket.sendto(b'\x08\x00\xf5\xfc\x01\x01\x01\x02', (dest_addr, 0))
        curr_addr = None
        curr_name = None
        try:
            curr_name, curr_addr = recv_socket.recvfrom(512)
            curr_addr = curr_addr[0]
            try:
                curr_name = socket.gethostbyaddr(curr_addr)[0]
            except socket.error:
                curr_name = curr_addr
        except socket.error:
            pass
        finally:
            send_socket.close()
            recv_socket.close()

        if curr_addr is not None:
            response.append([ttl, curr_addr, curr_name])
        else:
            response.append([ttl, None, None])

        ttl += 1
        if curr_name == dest_name or curr_addr == dest_addr or ttl > max_hops:
            break
    return response
