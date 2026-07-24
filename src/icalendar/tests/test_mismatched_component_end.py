import pytest

from icalendar.cal.calendar import Calendar


def test_mismatched_component_end_is_rejected():
    data = "BEGIN:VCALENDAR\r\nBEGIN:VEVENT\r\nEND:VTODO\r\nEND:VCALENDAR\r\n"

    with pytest.raises(ValueError, match=r"END:VTODO does not match BEGIN:VEVENT"):
        Calendar.from_ical(data)
