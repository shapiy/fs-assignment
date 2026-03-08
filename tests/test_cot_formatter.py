import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

from signal_atak_bot.config import Config
from signal_atak_bot.cot_formatter import format_cot_event
from signal_atak_bot.models import TargetReport


def _make_report(**kwargs) -> TargetReport:
    defaults = {
        "latitude": 48.567123,
        "longitude": 39.87897,
        "description": "tank",
        "uid": "test-uid-1234",
        "timestamp": datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
    }
    defaults.update(kwargs)
    return TargetReport(**defaults)


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


def test_valid_xml_output():
    report = _make_report()
    config = _make_config()
    xml_str = format_cot_event(report, config)
    root = ET.fromstring(xml_str)
    assert root.tag == "event"


def test_correct_lat_lon():
    report = _make_report(latitude=50.123, longitude=-30.456)
    config = _make_config()
    xml_str = format_cot_event(report, config)
    root = ET.fromstring(xml_str)
    point = root.find("point")
    assert point.get("lat") == "50.123"
    assert point.get("lon") == "-30.456"


def test_type_code_tank():
    report = _make_report(description="tank")
    config = _make_config()
    xml_str = format_cot_event(report, config)
    root = ET.fromstring(xml_str)
    assert root.get("type") == "a-h-G-U-C-A"


def test_type_code_infantry():
    report = _make_report(description="infantry patrol")
    config = _make_config()
    xml_str = format_cot_event(report, config)
    root = ET.fromstring(xml_str)
    assert root.get("type") == "a-h-G-U-C-I"


def test_type_code_default():
    report = _make_report(description="unknown thing")
    config = _make_config()
    xml_str = format_cot_event(report, config)
    root = ET.fromstring(xml_str)
    assert root.get("type") == "a-h-G"


def test_stale_time():
    ts = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    report = _make_report(timestamp=ts)
    config = _make_config(cot_stale_minutes=10)
    xml_str = format_cot_event(report, config)
    root = ET.fromstring(xml_str)

    expected_stale = (ts + timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%S")
    assert expected_stale in root.get("stale")


def test_uid_preserved():
    report = _make_report(uid="my-custom-uid")
    config = _make_config()
    xml_str = format_cot_event(report, config)
    root = ET.fromstring(xml_str)
    assert root.get("uid") == "my-custom-uid"


def test_detail_contains_callsign():
    report = _make_report(description="tank")
    config = _make_config(bot_callsign="ALPHA")
    xml_str = format_cot_event(report, config)
    root = ET.fromstring(xml_str)
    contact = root.find("detail/contact")
    assert contact.get("callsign") == "ALPHA-tank"


def test_detail_contains_remarks():
    report = _make_report(description="tank column")
    config = _make_config()
    xml_str = format_cot_event(report, config)
    root = ET.fromstring(xml_str)
    remarks = root.find("detail/remarks")
    assert "tank column" in remarks.text
