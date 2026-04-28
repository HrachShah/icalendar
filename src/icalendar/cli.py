#!/usr/bin/env python3
"""Utility program that allows user to preview calendar's events"""

import argparse
import sys
from datetime import datetime, date
from pathlib import Path
from typing import TextIO

from icalendar import __version__, vCalAddress
from icalendar.cal.calendar import Calendar
from icalendar.cal.event import Event


def _format_name(address: str | vCalAddress) -> str:
    """Format a display name and email from an address string.

    Parameters:
        address: An address object or string, such as mailto:name@example.com.

    Returns:
        A formatted string, like 'name <name@example.com>',
        or an empty string if no email is found.
    """
    address_str = str(address)
    if not address_str:
        return ""
    email = address_str.rsplit(":", maxsplit=1)[-1]
    if not email or "@" not in email:
        return ""
    return f"{email.split('@')[0]} <{email}>"


def _format_attendees(attendees: list | str | vCalAddress) -> str:
    """Format the list of attendees.

    Parameters:
        attendees: Either a list, a string, or a vCalAddress object.

    Returns:
        A formatted string of attendees, each indented by 5 spaces.
    """
    if isinstance(attendees, str):
        attendees = [attendees]
    return "\n".join(s.rjust(len(s) + 5) for s in map(_format_name, attendees or []))


def view(event: Event) -> str:
    """Make a human readable summary of an iCalendar file.

    Parameters:
        event: An iCalendar event containing fields such as
               summary, organizer, attendees, location, and timing.

    Returns:
        A human readable summary of the event.
    """
    summary = event.get("summary", default="")
    organizer = _format_name(event.get("organizer", default=""))
    attendees = _format_attendees(event.get("attendee", default=[]))
    location = event.get("location", default="")
    comment = event.get("comment", "")
    description = event.get("description", "").split("\n")
    description = "\n".join(s.rjust(len(s) + 5) for s in description)

    start = event.decoded("dtstart", default=None)
    end = None
    if start is not None:
        if "duration" in event:
            end = event.decoded("dtend", default=start + event.decoded("duration"))
        else:
            end = event.decoded("dtend", default=start)
    duration = event.decoded("duration", default=None)
    if start and end and duration is None:
        duration = end - start if isinstance(end, type(start)) else ""
    if isinstance(start, datetime):
        start = start.astimezone()
        start = start.strftime("%c")
    elif isinstance(start, date):
        start = start.strftime("%c")  # e.g. "Wed May 11 00:00:00 2022"
    else:
        start = str(start) if start else ""
    if isinstance(end, datetime):
        end = end.astimezone()
        end = end.strftime("%c")
    elif isinstance(end, date):
        end = end.strftime("%c")
    else:
        end = str(end) if end else ""

    return f"""    Organizer: {organizer}
    Attendees:
{attendees}
    Summary    : {summary}
    Starts     : {start}
    End        : {end}
    Duration   : {duration}
    Location   : {location}
    Comment    : {comment}
    Description:
{description}"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "calendar_files", nargs="+", help="one or more .ics files (use '-' for stdin)"
    )

    parser.add_argument(
        "--output", "-o", default="-", help="output file path (use '-' for stdout)"
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"{parser.prog} version {__version__}",
    )

    argv = parser.parse_args()

    # Use context managers for automatic and reliable resource cleanup.
    # This avoids the fragile flag-variable pattern that can leave files
    # open or raise NameError when exceptions occur before flags are set.
    if argv.output == "-":
        output_file: TextIO = sys.stdout
        for path in argv.calendar_files:
            f = sys.stdin if path == "-" else Path(path).open(encoding="utf-8-sig")
            try:
                calendar = Calendar.from_ical(f.read())
                output_file.writelines(
                    view(event) + "\n\n" for event in calendar.walk("vevent")
                )
            finally:
                if path != "-":
                    f.close()
    else:
        with Path(argv.output).open("w", encoding="utf-8") as output_file:
            for path in argv.calendar_files:
                with Path(path).open(encoding="utf-8-sig") as f:
                    calendar = Calendar.from_ical(f.read())
                    output_file.writelines(
                        view(event) + "\n\n" for event in calendar.walk("vevent")
                    )


__all__ = ["main", "view"]

if __name__ == "__main__":
    main()
