import xml.etree.ElementTree as ET

from signal_atak_bot.config import Config
from signal_atak_bot.cot_formatter import format_cot_event
from signal_atak_bot.signal_handler import parse_target_message


def _make_config(**kwargs) -> Config:
    defaults = {
        "signal_tcp_host": "localhost",
        "signal_tcp_port": 7583,
        "signal_http_url": "http://localhost:8080",
        "signal_account": "+1234567890",
        "atak_host": "239.2.3.1",
        "atak_port": 6969,
        "atak_use_multicast": True,
        "cot_stale_minutes": 5,
        "bot_callsign": "SIGBOT",
    }
    defaults.update(kwargs)
    return Config(**defaults)


def test_full_pipeline_parse_to_cot():
    """Parse a message, format CoT, and validate the full XML output."""
    report = parse_target_message("48.567123 39.87897 tank")
    config = _make_config()

    xml_str = format_cot_event(report, config)
    root = ET.fromstring(xml_str)

    assert root.tag == "event"
    assert root.get("type") == "a-h-G-U-C-A"
    assert root.get("how") == "h-g-i-g-o"

    point = root.find("point")
    assert point.get("lat") == "48.567123"
    assert point.get("lon") == "39.87897"

    contact = root.find("detail/contact")
    assert "tank" in contact.get("callsign")


def test_pipeline_with_unknown_target():
    report = parse_target_message("50.0 30.0 checkpoint")
    config = _make_config()

    xml_str = format_cot_event(report, config)
    root = ET.fromstring(xml_str)

    assert root.get("type") == "a-h-G"
