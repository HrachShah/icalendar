from datetime import date, datetime, timezone

import pytest

from icalendar import Event, Journal, Todo
from icalendar.error import InvalidCalendar
from icalendar.prop import vText

RECURRENCE_COMPONENTS = (Event, Todo, Journal)


@pytest.fixture(params=RECURRENCE_COMPONENTS)
def component(request):
    """Return an instance of a component that can have a RECURRENCE-ID."""
    return request.param()


def test_recurrence_id_absent_returns_none(component):
    """RECURRENCE-ID returns None if the property is absent."""
    assert component.recurrence_id is None


def test_recurrence_id_returns_datetime(component):
    """RECURRENCE-ID returns the datetime if it is present."""
    dt = datetime(2025, 4, 28, 16, 5)
    component.recurrence_id = dt
    assert component.recurrence_id == dt
    assert component["RECURRENCE-ID"].dt == dt


def test_recurrence_id_returns_date(component):
    """RECURRENCE-ID returns the date if it is present."""
    d = date(2025, 4, 28)
    component.recurrence_id = d
    assert component.recurrence_id == d
    assert component["RECURRENCE-ID"].dt == d


def test_recurrence_id_invalid_type_raises(component):
    """RECURRENCE-ID raises TypeError if the value is not a date or datetime."""
    with pytest.raises(TypeError):
        component.recurrence_id = "not-a-date"


def test_recurrence_id_invalid_raw_value_raises_invalid_calendar(component):
    """Invalid raw value in RECURRENCE-ID raises InvalidCalendar."""
    component["RECURRENCE-ID"] = "not-a-date"

    with pytest.raises(InvalidCalendar):
        _ = component.recurrence_id


def test_recurrence_id_invalid_vprop_raises_invalid_calendar(component):
    """Invalid vProp in RECURRENCE-ID raises InvalidCalendar."""
    component["RECURRENCE-ID"] = vText("some text")

    with pytest.raises(InvalidCalendar):
        _ = component.recurrence_id


def test_recurrence_id_set_none_deletes_property(component):
    """Setting RECURRENCE-ID to None removes the property."""
    dt = datetime(2025, 4, 28, 16, 5)
    component.recurrence_id = dt
    assert "RECURRENCE-ID" in component

    component.recurrence_id = None

    assert component.recurrence_id is None
    assert "RECURRENCE-ID" not in component


def test_recurrence_id_del_deletes_property(component):
    """Deleting RECURRENCE-ID removes the property."""
    dt = datetime(2025, 4, 28, 16, 5)
    component.recurrence_id = dt
    assert "RECURRENCE-ID" in component

    del component["RECURRENCE-ID"]

    assert component.recurrence_id is None
    assert "RECURRENCE-ID" not in component


def test_recurrence_id_with_timezone_in_to_ical(component):
    """RECURRENCE-ID with timezone is preserved in to_ical()."""
    dt = datetime(2025, 4, 28, 16, 5, tzinfo=timezone.utc)
    component.recurrence_id = dt

    ical_bytes = component.to_ical()
    lines = ical_bytes.splitlines()

    assert any(
        line.startswith((b"RECURRENCE-ID;TZID=", b"RECURRENCE-ID:20250428T160500Z"))
        for line in lines
    )


def test_recurrence_id_parsed_from_calendar(calendars):
    """RECURRENCE-ID is correctly parsed from existing calendars."""
    cal = calendars["issue_1231_recurrence"]

    components = [
        c for c in cal.walk()
        if c.name in {"VEVENT", "VTODO", "VJOURNAL"} and "RECURRENCE-ID" in c
    ]
    assert components, "Expected at least one component with RECURRENCE-ID"

    comp = components[0]

    expected = datetime(2025, 4, 28, 16, 5, tzinfo=timezone.utc)

    assert comp.recurrence_id == expected
    assert comp["RECURRENCE-ID"].dt == expected
