import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from icalendar import Calendar, cli, vCalAddress

INPUT = """
BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
BEGIN:VEVENT
SUMMARY:Test Summary
ORGANIZER:organizer@test.test
ATTENDEE:attendee1@example.com
ATTENDEE:attendee2@test.test
COMMENT:Comment
DTSTART;TZID=Europe/Warsaw:20220820T103400
DTEND;TZID=Europe/Warsaw:20220820T113400
LOCATION:New Amsterdam, 1000 Sunrise Test Street
DESCRIPTION: Test Description
END:VEVENT
BEGIN:VEVENT
ORGANIZER:organizer@test.test
ATTENDEE:attendee1@example.com
SUMMARY:Test summary
DTSTART;TZID=Europe/Warsaw:20220820T200000
DTEND;TZID=Europe/Warsaw:20220820T203000
LOCATION:New Amsterdam, 1010 Test Street
DESCRIPTION:Test Description\\nThis one is multiline
END:VEVENT
BEGIN:VEVENT
UID:1
SUMMARY:TEST
DTSTART:20220511
DURATION:P5D
END:VEVENT
END:VCALENDAR
"""


def local_datetime(dt):
    return (
        datetime.strptime(dt, "%Y%m%dT%H%M%S")
        .replace(tzinfo=ZoneInfo("Europe/Warsaw"))
        .astimezone()
        .strftime("%c")
    )


# datetimes are displayed in the local timezone, so we cannot just hardcode them
firststart = local_datetime("20220820T103400")
firstend = local_datetime("20220820T113400")
secondstart = local_datetime("20220820T200000")
secondend = local_datetime("20220820T203000")

PROPER_OUTPUT = f"""    Organizer: organizer <organizer@test.test>
    Attendees:
     attendee1 <attendee1@example.com>
     attendee2 <attendee2@test.test>
    Summary    : Test Summary
    Starts     : {firststart}
    End        : {firstend}
    Duration   : 1:00:00
    Location   : New Amsterdam, 1000 Sunrise Test Street
    Comment    : Comment
    Description:
      Test Description

    Organizer: organizer <organizer@test.test>
    Attendees:
     attendee1 <attendee1@example.com>
    Summary    : Test summary
    Starts     : {secondstart}
    End        : {secondend}
    Duration   : 0:30:00
    Location   : New Amsterdam, 1010 Test Street
    Comment    : 
    Description:
     Test Description
     This one is multiline

    Organizer: 
    Attendees:

    Summary    : TEST
    Starts     : Wed May 11 00:00:00 2022
    End        : Mon May 16 00:00:00 2022
    Duration   : 5 days, 0:00:00
    Location   : 
    Comment    : 
    Description:
     

"""  # noqa: W291, W293


class CLIToolTest(unittest.TestCase):
    def test_output_is_proper(self):
        self.maxDiff = None
        calendar = Calendar.from_ical(INPUT)
        output = ""
        for event in calendar.walk("vevent"):
            output += cli.view(event) + "\n\n"
        assert output == PROPER_OUTPUT


class FormatNameTest(unittest.TestCase):
    """Tests for :func:`cli._format_name` covering CN param and string inputs."""

    def test_vcaladdress_with_cn_uses_cn(self):
        addr = vCalAddress("mailto:jane@example.com", params={"CN": "Jane Doe"})
        assert cli._format_name(addr) == "Jane Doe <jane@example.com>"

    def test_vcaladdress_without_cn_falls_back_to_localpart(self):
        addr = vCalAddress("mailto:bob@example.com")
        assert cli._format_name(addr) == "bob <bob@example.com>"

    def test_plain_string_with_mailto_prefix_strips_prefix(self):
        assert cli._format_name("mailto:carol@example.com") == "carol <carol@example.com>"

    def test_plain_string_without_mailto_prefix_keeps_email(self):
        assert cli._format_name("dave@example.com") == "dave <dave@example.com>"

    def test_empty_string_returns_empty(self):
        assert cli._format_name("") == ""


if __name__ == "__main__":
    unittest.main()
