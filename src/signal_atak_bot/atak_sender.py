import socket
import struct


def send_cot(cot_xml: str, host: str, port: int, multicast: bool = False) -> None:
    data = cot_xml.encode("utf-8")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        if multicast:
            ttl = struct.pack("b", 32)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
        sock.sendto(data, (host, port))
