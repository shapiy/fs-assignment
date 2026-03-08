import xml.etree.ElementTree as ET
from datetime import timedelta

from .config import Config
from .models import TargetReport

# MIL-STD-2525 CoT type codes for common targets
COT_TYPE_MAP = {
    "tank": "a-h-G-U-C-A",
    "infantry": "a-h-G-U-C-I",
    "vehicle": "a-h-G-U-C-V",
    "artillery": "a-h-G-U-C-F",
    "apc": "a-h-G-U-C-A-W",
    "helicopter": "a-h-A-C-H",
    "drone": "a-h-A-C-F-q",
    "ship": "a-h-S",
    "sniper": "a-h-G-U-C-I-s",
    "sam": "a-h-G-U-C-D-A",
}

DEFAULT_COT_TYPE = "a-h-G"


def _cot_time(dt) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _resolve_cot_type(description: str) -> str:
    first_word = description.strip().split()[0].lower() if description.strip() else ""
    return COT_TYPE_MAP.get(first_word, DEFAULT_COT_TYPE)


def format_cot_event(report: TargetReport, config: Config) -> str:
    start = report.timestamp
    stale = start + timedelta(minutes=config.cot_stale_minutes)

    event = ET.Element("event")
    event.set("version", "2.0")
    event.set("type", _resolve_cot_type(report.description))
    event.set("uid", report.uid)
    event.set("how", "h-g-i-g-o")
    event.set("time", _cot_time(start))
    event.set("start", _cot_time(start))
    event.set("stale", _cot_time(stale))

    point = ET.SubElement(event, "point")
    point.set("lat", str(report.latitude))
    point.set("lon", str(report.longitude))
    point.set("hae", "0")
    point.set("ce", "9999999")
    point.set("le", "9999999")

    detail = ET.SubElement(event, "detail")
    contact = ET.SubElement(detail, "contact")
    contact.set("callsign", f"{config.bot_callsign}-{report.description}")
    remarks = ET.SubElement(detail, "remarks")
    remarks.text = f"Reported via Signal: {report.description}"

    return ET.tostring(event, encoding="unicode", xml_declaration=True)
