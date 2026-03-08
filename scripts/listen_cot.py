#!/usr/bin/env python3
"""Mock ATAK receiver: listens for CoT XML on UDP and prints it."""

import argparse
import socket
import struct


def main():
    parser = argparse.ArgumentParser(description="Listen for CoT events on UDP")
    parser.add_argument("--host", default="239.2.3.1", help="Multicast group or bind address (default: 239.2.3.1)")
    parser.add_argument("--port", type=int, default=6969, help="UDP port (default: 6969)")
    parser.add_argument("--unicast", action="store_true", help="Listen in unicast mode")
    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    if args.unicast:
        sock.bind(("", args.port))
    else:
        sock.bind(("", args.port))
        mreq = struct.pack("4sL", socket.inet_aton(args.host), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print(f"Listening for CoT on {'unicast' if args.unicast else 'multicast ' + args.host}:{args.port}")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            data, addr = sock.recvfrom(65535)
            print(f"--- Received from {addr[0]}:{addr[1]} ---")
            print(data.decode("utf-8", errors="replace"))
            print()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
