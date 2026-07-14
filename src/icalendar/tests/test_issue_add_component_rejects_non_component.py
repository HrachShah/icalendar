"""Component.add_component() should reject non-Component values with a clear TypeError.

The subcomponents list is type-hinted as ``list[Component]`` and downstream
serialization code (to_ical, walk) calls Component-specific methods on whatever
is stored there, so a stray non-Component entry used to crash later with
``AttributeError: 'str' object has no attribute 'property_items'``. The fix
surfaces the type error at the call site.
"""

import pytest

from icalendar import Calendar, Event


def test_add_component_rejects_str():
    cal = Calendar()
    with pytest.raises(TypeError, match="add_component requires a Component"):
        cal.add_component("not a component")


def test_add_component_rejects_none():
    cal = Calendar()
    with pytest.raises(TypeError, match="add_component requires a Component"):
        cal.add_component(None)


def test_add_component_rejects_dict():
    cal = Calendar()
    with pytest.raises(TypeError, match="add_component requires a Component"):
        cal.add_component({"SUMMARY": "nope"})


def test_add_component_rejects_int():
    cal = Calendar()
    with pytest.raises(TypeError, match="add_component requires a Component"):
        cal.add_component(42)


def test_add_component_accepts_component():
    cal = Calendar()
    event = Event()
    cal.add_component(event)
    assert cal.subcomponents == [event]


def test_add_component_error_message_includes_type_and_repr():
    cal = Calendar()
    with pytest.raises(TypeError) as exc_info:
        cal.add_component("hello")
    msg = str(exc_info.value)
    assert "add_component requires a Component" in msg
    assert "str" in msg
    assert "'hello'" in msg
