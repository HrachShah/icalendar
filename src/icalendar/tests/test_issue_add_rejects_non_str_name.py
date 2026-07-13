"""Component.add() should reject non-str names with a clear TypeError.

Component.add() is the canonical way to attach a property to a calendar
component. The implementation forwards ``name`` to the property type
factory, which immediately calls ``name.upper()``. Passing a non-str
``name`` therefore surfaces as an opaque ``AttributeError: 'int'
object has no attribute 'upper'`` (or 'NoneType', or 'list', etc.)
from the type-factory layer rather than at the offending call site.

This test guards the explicit TypeError so callers get a clear,
immediate error naming the bad value's type and repr.
"""

from __future__ import annotations

import pytest

from icalendar import Calendar, Event


@pytest.mark.parametrize("bad_name", [123, None, 4.5, ("summary",), b"summary"])
def test_component_add_rejects_non_str_name(bad_name) -> None:
    """add() should raise TypeError when name is not a str."""
    cal = Calendar()
    evt = Event()
    with pytest.raises(TypeError, match="add"):
        evt.add(bad_name, "x")  # type: ignore[arg-type]


def test_component_add_non_str_name_does_not_crash_factory() -> None:
    """The pre-fix error was 'AttributeError' from the property factory.

    The fix should replace that with a TypeError that names the bad
    value at the call site, so a debug session can find the offending
    add() line directly from the traceback.
    """
    cal = Calendar()
    evt = Event()
    with pytest.raises(TypeError) as excinfo:
        evt.add(None, "x")  # type: ignore[arg-type]
    # The error message should mention the bad value's type and repr
    msg = str(excinfo.value)
    assert "NoneType" in msg
    assert "None" in msg


def test_component_add_str_name_still_works() -> None:
    """The type check must not break the happy path."""
    evt = Event()
    evt.add("summary", "Team sync")
    assert str(evt["summary"]) == "Team sync"
