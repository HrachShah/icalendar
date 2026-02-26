"""UTC datetimes must not generate a spurious VTIMEZONE component.

Per :rfc:`5545` section 3.2.19, the TZID parameter MUST NOT be applied to
DATE-TIME or TIME properties whose time values are specified in UTC.

See https://github.com/collective/icalendar/issues/1124
"""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from icalendar import Calendar, Event, Timezone


def test_add_missing_timezones_does_not_generate_utc():
    """add_missing_timezones() must not add a VTIMEZONE for UTC.

    Using new(), we set DTSTAMP which is in UTC.
    This tests that the UTC timezone is not added.
    """
    event = Event.new(
        summary="Meeting in Zurich",
        start=datetime(2022, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("Europe/Zurich")),
        end=datetime(2022, 1, 1, 13, 0, 0, tzinfo=ZoneInfo("Europe/Zurich")),
    )
    calendar = Calendar.new(subcomponents=[event])
    calendar.add_missing_timezones()
    tz_names = [tz.tz_name for tz in calendar.timezones]
    assert "UTC" not in tz_names
    assert "Europe/Zurich" in tz_names


def test_utc_not_in_used_tzids():
    """UTC must not appear in get_used_tzids() — it uses the Z suffix, not a TZID."""
    event = Event.new(
        summary="test",
        start=datetime(2022, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        end=datetime(2022, 1, 1, 13, 0, 0, tzinfo=timezone.utc),
    )
    calendar = Calendar.new(subcomponents=[event])
    assert "UTC" not in calendar.get_used_tzids()


def test_get_missing_tzids_does_not_crash_with_extra_vtimezone():
    """get_missing_tzids() must not crash when a VTIMEZONE exists for a TZID
    not referenced by any event property (e.g. added externally)."""
    calendar = Calendar()
    tz = Timezone.from_tzid("America/New_York")
    calendar.add_component(tz)
    # No events reference America/New_York — discard must not raise KeyError
    assert calendar.get_missing_tzids() == set()
