"""Test vDDDLists."""

import pytest

from icalendar.prop.dt.list import vDDDLists


def test_from_ical_validation():
    """from_ical should reject non-str/bytes inputs with a clear ValueError naming the type."""
    with pytest.raises(ValueError) as exc_info:
        vDDDLists.from_ical(1)
    assert "int" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        vDDDLists.from_ical(None)
    assert "NoneType" in str(exc_info.value)
    assert "None" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        vDDDLists.from_ical([1, 2])
    assert "list" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        vDDDLists.from_ical({"x": 1})
    assert "dict" in str(exc_info.value)

    # valid string input still works
    out = vDDDLists.from_ical("20210302T101500,20210302T111500")
    assert len(out) == 2
