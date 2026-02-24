from datetime import date, datetime

import pytest

from icalendar import Event, Journal, Todo

RECURRENCE_COMPONENTS = (Event, Todo, Journal)


@pytest.fixture(params=RECURRENCE_COMPONENTS)
def component(request):
    """Return an instance of a component that can have a RECURRENCE-ID."""
    return request.param()


def test_recurrence_id_absent_returns_none(component):
    """RECURRENCE-ID returns None if the property is absent."""
    assert component.recurrence_id is None


def test_recurrence_id_returns_datetime(component):
    """RECURRENCE-ID returns the date or date-time if it is present."""
    dt = datetime(2025, 4, 28, 16, 5)
    component.recurrence_id = dt
    assert component.recurrence_id == dt
    assert component["RECURRENCE-ID"].dt == dt

    d = date(2025, 4, 28)
    component.recurrence_id = d
    assert component.recurrence_id == d
    assert component["RECURRENCE-ID"].dt == d


def test_recurrence_id_invalid_type_raises(component):
    """RECURRENCE-ID raises TypeError if the value is not a date or datetime."""
    with pytest.raises(TypeError):
        component.recurrence_id = "not-a-date"
