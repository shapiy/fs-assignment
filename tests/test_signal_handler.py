import pytest

from signal_atak_bot.signal_handler import parse_target_message


def test_parse_valid_message():
    report = parse_target_message("48.567123 39.87897 tank")
    assert report.latitude == 48.567123
    assert report.longitude == 39.87897
    assert report.description == "tank"


def test_parse_negative_coords():
    report = parse_target_message("-33.8688 151.2093 vehicle convoy")
    assert report.latitude == -33.8688
    assert report.longitude == 151.2093
    assert report.description == "vehicle convoy"


def test_parse_multi_word_description():
    report = parse_target_message("50.0 30.0 tank column moving north")
    assert report.description == "tank column moving north"


def test_parse_integer_coords():
    report = parse_target_message("50 30 infantry")
    assert report.latitude == 50.0
    assert report.longitude == 30.0


def test_parse_with_extra_whitespace():
    report = parse_target_message("  48.5  39.8  tank  ")
    assert report.latitude == 48.5
    assert report.longitude == 39.8
    assert report.description == "tank"


def test_parse_invalid_format():
    with pytest.raises(ValueError, match="Invalid format"):
        parse_target_message("hello world")


def test_parse_missing_description():
    with pytest.raises(ValueError, match="Invalid format"):
        parse_target_message("48.5 39.8")


def test_parse_empty_string():
    with pytest.raises(ValueError, match="Invalid format"):
        parse_target_message("")


def test_parse_lat_out_of_range():
    with pytest.raises(ValueError, match="Latitude"):
        parse_target_message("91.0 39.0 tank")


def test_parse_lon_out_of_range():
    with pytest.raises(ValueError, match="Longitude"):
        parse_target_message("48.0 181.0 tank")


def test_parse_negative_lat_out_of_range():
    with pytest.raises(ValueError, match="Latitude"):
        parse_target_message("-91.0 39.0 tank")


def test_uid_auto_generated():
    report = parse_target_message("48.5 39.8 tank")
    assert report.uid is not None
    assert len(report.uid) > 0
