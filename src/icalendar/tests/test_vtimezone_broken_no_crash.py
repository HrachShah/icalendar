"""Regression tests: a broken VTIMEZONE (TZID present but no usable
STANDARD/DAYLIGHT subcomponents) should not crash the whole
``Calendar.from_ical`` call. Previously, ``handle_end_component`` called
``tzp.cache_timezone_component`` unconditionally for any ``END:VTIMEZONE``
that had a ``TZID``, and that path raises ``ValueError`` ("at least one
component is needed") from inside ``dateutil.tz.tzical`` when the
VTIMEZONE has no STANDARD/DAYLIGHT subcomponents, or ("mandatory DTSTART
not found") when the subcomponent is structurally present but empty.

The fix wraps the cache call in a try/except for the failure modes
dateutil/icalendar can actually raise (``ValueError``, ``KeyError``,
``TypeError``, ``OSError``), records the failure on the component's
``errors`` list, and lets the parse continue. The broken VTIMEZONE is
preserved verbatim in the parsed tree so the caller can still
serialize it.
"""

import pytest

from icalendar import Calendar


EMPTY_VTIMEZONE_TZID = (
    "BEGIN:VCALENDAR\r\n"
    "VERSION:2.0\r\n"
    "PRODID:-//Test//Test//EN\r\n"
    "BEGIN:VTIMEZONE\r\n"
    "TZID:Empty\r\n"
    "END:VTIMEZONE\r\n"
    "END:VCALENDAR\r\n"
)


EMPTY_STANDARD_VTIMEZONE = (
    "BEGIN:VCALENDAR\r\n"
    "VERSION:2.0\r\n"
    "PRODID:-//Test//Test//EN\r\n"
    "BEGIN:VTIMEZONE\r\n"
    "TZID:Bad\r\n"
    "BEGIN:STANDARD\r\n"
    "END:STANDARD\r\n"
    "END:VTIMEZONE\r\n"
    "END:VCALENDAR\r\n"
)


VALID_VTIMEZONE = (
    "BEGIN:VCALENDAR\r\n"
    "VERSION:2.0\r\n"
    "PRODID:-//Test//Test//EN\r\n"
    "BEGIN:VTIMEZONE\r\n"
    "TZID:US-Eastern\r\n"
    "BEGIN:STANDARD\r\n"
    "DTSTART:19671105T020000\r\n"
    "RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU\r\n"
    "TZNAME:EST\r\n"
    "TZOFFSETFROM:-0400\r\n"
    "TZOFFSETTO:-0500\r\n"
    "END:STANDARD\r\n"
    "END:VTIMEZONE\r\n"
    "END:VCALENDAR\r\n"
)


def test_empty_vtimezone_with_tzid_does_not_crash_from_ical():
    """VTIMEZONE with TZID but no STANDARD/DAYLIGHT previously crashed the
    whole from_ical with ValueError('at least one component is needed') from
    inside dateutil.tz.tzical. The fix records the error on the component
    and continues."""
    cal = Calendar.from_ical(EMPTY_VTIMEZONE_TZID)
    vtz_list = cal.walk("VTIMEZONE")
    assert len(vtz_list) == 1
    vtz = vtz_list[0]
    assert vtz["TZID"].to_ical() == b"Empty"
    # The component-level error is recorded instead of raising.
    assert any("Failed to cache VTIMEZONE" in msg for _, msg in vtz.errors)
    # The broken VTIMEZONE is still serialized by to_ical (preserved verbatim).
    out = cal.to_ical()
    assert b"BEGIN:VTIMEZONE" in out
    assert b"TZID:Empty" in out


def test_vtimezone_with_empty_standard_subcomponent_does_not_crash():
    """A VTIMEZONE that has a STANDARD subcomponent but the subcomponent is
    empty (no DTSTART) used to crash from_ical with 'mandatory DTSTART not
    found'. Same fix path."""
    cal = Calendar.from_ical(EMPTY_STANDARD_VTIMEZONE)
    vtz = cal.walk("VTIMEZONE")[0]
    assert vtz["TZID"].to_ical() == b"Bad"
    assert any("Failed to cache VTIMEZONE" in msg for _, msg in vtz.errors)


def test_valid_vtimezone_still_caches_without_error():
    """Sanity check: a structurally valid VTIMEZONE is still cached and no
    error is recorded."""
    cal = Calendar.from_ical(VALID_VTIMEZONE)
    vtz = cal.walk("VTIMEZONE")[0]
    assert vtz["TZID"].to_ical() == b"US-Eastern"
    # No component-level error for a valid VTIMEZONE.
    assert vtz.errors == []


def test_broken_vtimezone_followed_by_valid_event_roundtrips():
    """The most common real-world case: a calendar with a broken VTIMEZONE
    (or a stray one with no subcomponents) plus real events. Previously the
    whole parse would fail and the events would be lost. Now the events
    parse, the broken VTIMEZONE is preserved, and to_ical round-trips."""
    ics = (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "PRODID:-//Test//Test//EN\r\n"
        "BEGIN:VTIMEZONE\r\n"
        "TZID:Empty\r\n"
        "END:VTIMEZONE\r\n"
        "BEGIN:VEVENT\r\n"
        "UID:event-1@example.com\r\n"
        "DTSTAMP:20250101T000000Z\r\n"
        "DTSTART:20250102T100000Z\r\n"
        "SUMMARY:Real event after broken VTIMEZONE\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )
    cal = Calendar.from_ical(ics)
    events = cal.walk("VEVENT")
    assert len(events) == 1
    assert events[0]["SUMMARY"].to_ical() == b"Real event after broken VTIMEZONE"
    out = cal.to_ical()
    assert b"VEVENT" in out
    assert b"Real event after broken VTIMEZONE" in out
