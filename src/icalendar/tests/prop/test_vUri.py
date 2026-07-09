import pytest

from icalendar.prop import vUri


def test_from_ical_accepts_string():
    """vUri.from_ical parses a plain URI string."""
    assert vUri.from_ical("http://example.com/foo") == "http://example.com/foo"


def test_from_ical_accepts_bytes():
    """vUri.from_ical decodes bytes to a URI string."""
    assert vUri.from_ical(b"http://example.com/foo") == "http://example.com/foo"


def test_from_ical_mentions_uri_in_error_message():
    """vUri.from_ical surfaces a clear ValueError that names the URI type.

    The error message used to read "Expected , got: <value>" because the
    type name was missing from the format string. It now reads
    "Expected URI, got: <repr(value)>" so a caller catching ValueError
    actually learns the offending property is a URI.
    """
    class BadInput:
        def __str__(self):
            raise RuntimeError("str() exploded")

    with pytest.raises(ValueError, match="Expected URI, got:"):
        vUri.from_ical(BadInput())
