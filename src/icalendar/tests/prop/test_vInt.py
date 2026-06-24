import pytest

from icalendar.prop.integer import vInt


def test_zero():
    assert vInt(0).to_ical() == b"0"


def test_roundtrip():
    assert vInt.from_ical(vInt("42").to_ical()) == 42
    assert vInt.from_ical("42") == 42


def test_error():
    """Error: not an integer string"""
    with pytest.raises(ValueError):
        vInt.from_ical("not an int")


def test_ical_value():
    """ical_value property returns the int value."""
    assert vInt(1).ical_value == 1
    assert vInt(0).ical_value == 0


@pytest.mark.parametrize("value", [1.5, 0.1, 3.0, 1e20, -0.5])
def test_from_ical_rejects_floats(value):
    """Floats must raise - int(1.5) silently truncates to 1."""
    with pytest.raises(ValueError):
        vInt.from_ical(value)