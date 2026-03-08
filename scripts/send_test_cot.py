#!/usr/bin/env python3
"""CLI tool to send a test CoT event to ATAK without Signal."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from signal_atak_bot.atak_sender import send_cot
from signal_atak_bot.config import Config
from signal_atak_bot.cot_formatter import format_cot_event
from signal_atak_bot.models import TargetReport


def main():
    parser = argparse.ArgumentParser(description="Send a test CoT event to ATAK")
    parser.add_argument("lat", type=float, help="Latitude")
    parser.add_argument("lon", type=float, help="Longitude")
    parser.add_argument("description", nargs="+", help="Target description")
    parser.add_argument("--host", default="239.2.3.1", help="ATAK host (default: 239.2.3.1)")
    parser.add_argument("--port", type=int, default=6969, help="ATAK port (default: 6969)")
    parser.add_argument("--unicast", action="store_true", help="Use unicast instead of multicast")
    args = parser.parse_args()

    description = " ".join(args.description)
    report = TargetReport(latitude=args.lat, longitude=args.lon, description=description)
    config = Config(atak_host=args.host, atak_port=args.port)

    cot_xml = format_cot_event(report, config)
    print(f"Sending CoT to {args.host}:{args.port}:")
    print(cot_xml)

    send_cot(cot_xml, args.host, args.port, multicast=not args.unicast)
    print("Sent.")


if __name__ == "__main__":
    main()
