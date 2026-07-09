from datetime import date, datetime, time, timedelta

import pytest

from icalendar.prop import vDDDTypes


def test_instance():
    assert isinstance(vDDDTypes.from_ical("20010101T123000"), datetime)
    assert isinstance(vDDDTypes.from_ical("20010101"), date)


def test_datetime_with_timezone(tzp):
    assert vDDDTypes.from_ical("20010101T123000Z") == tzp.localize_utc(
        datetime(2001, 1, 1, 12, 30)
    )


def test_timedelta():
    assert vDDDTypes.from_ical("P31D") == timedelta(31)
    assert vDDDTypes.from_ical("-P31D") == timedelta(-31)


def test_bad_input():
    with pytest.raises(TypeError):
        vDDDTypes(42)


def test_time_from_string():
    assert vDDDTypes.from_ical("123000") == time(12, 30)
    assert isinstance(vDDDTypes.from_ical("123000"), time)


def test_invalid_period_to_ical():
    invalid_period = (datetime(2000, 1, 1), datetime(2000, 1, 2), datetime(2000, 1, 2))
    with pytest.raises(ValueError):
        vDDDTypes(invalid_period).to_ical()


def test_from_ical_validation():
    """from_ical should reject non-str/bytes inputs with a clear ValueError naming the type."""
    with pytest.raises(ValueError) as exc_info:
        vDDDTypes.from_ical(1)
    assert "int" in str(exc_info.value)
    # repr(1) is '1'; assert the value surfaces in the message
    assert "1" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        vDDDTypes.from_ical(None)
    assert "NoneType" in str(exc_info.value)
    assert "None" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        vDDDTypes.from_ical([1, 2])
    assert "list" in str(exc_info.value)
    assert "[1, 2]" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        vDDDTypes.from_ical({"x": 1})
    assert "dict" in str(exc_info.value)
    assert "{'x': 1}" in str(exc_info.value)

    # Sanity check: valid str/bytes inputs still parse
    assert isinstance(vDDDTypes.from_ical("20010101T123000"), datetime)
    assert isinstance(vDDDTypes.from_ical(b"20010101T123000"), datetime)
    assert isinstance(vDDDTypes.from_ical("20010101"), date)
