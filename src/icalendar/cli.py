#!/usr/bin/env python3
"""Utility program that allows user to preview calendar's events"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from icalendar import __version__, vCalAddress
from icalendar.cal.calendar import Calendar
from icalendar.cal.event import Event


def _format_name(address: str) -> str:
    """Format a display name and email from an address string.

    Parameters:
        address: An address object, such as mailto:name@example.com,
            a vCalAddress object, a CN= display name (with optional mailto:),
            or None.

    Returns:
        A formatted string, like 'name <name@example.com>',
        or an empty string if no email is found.
    """
    if address is None:
        return ""

    display_name = None

    # Handle CN= display name format, e.g. "CN=John Doe,mailto:john@example.com"
    # or "CN=John Doe (guest)"
    if address.startswith("CN="):
        parts = address.split(",", 1)
        display_name = parts[0][3:].strip()  # Remove "CN=" prefix
        # If there's a mailto: part after the comma, use its email
        if len(parts) > 1:
            email = parts[1].rsplit("mailto:", 1)[-1]
        else:
            email = None
    else:
        # Strip mailto: prefix for consistent parsing
        stripped = address.rsplit("mailto:", 1)[-1]
        email = stripped if "@" in stripped else None

    if not email:
        return display_name or ""

    if not display_name:
        display_name = email.split("@")[0]

    return f"{display_name} <{email}>"

def _format_attendees(attendees: list | str | vCalAddress) -> str:
    """Format the list of attendees.

    Parameters:
        attendees: Either a list, a string, or a vCalAddress object.

    Returns:
        A formatted string of attendees, each indented by 5 spaces.
    """
    if isinstance(attendees, str):
        attendees = [attendees]
    return "\n".join(s.rjust(len(s) + 5) for s in map(_format_name, attendees))


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

    start = event.decoded("dtstart")
    if "duration" in event:
        end = event.decoded("dtend", default=start + event.decoded("duration"))
    else:
        end = event.decoded("dtend", default=start)
    duration = event.decoded("duration", default=end - start)
    if isinstance(start, datetime):
        start = start.astimezone()
    start = start.strftime("%c")
    if isinstance(end, datetime):
        end = end.astimezone()
    end = end.strftime("%c")

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

    # Open output file
    if argv.output == "-":
        output_file = sys.stdout
    else:
        output_file = Path(argv.output).open("w", encoding="utf-8")  # noqa: SIM115

    try:
        # Iterate over input paths
        for path in argv.calendar_files:
            if path == "-":
                f = sys.stdin
            else:
                f = Path(path).open(encoding="utf-8-sig")  # noqa: SIM115

            try:
                calendar = Calendar.from_ical(f.read())
                output_file.writelines(
                    view(event) + "\n\n" for event in calendar.walk("vevent")
                )
            finally:
                if f is not sys.stdin:
                    f.close()
    finally:
        if argv.output != "-":
            output_file.close()


__all__ = ["main", "view"]

if __name__ == "__main__":
    main()
