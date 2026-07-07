import unittest

import icalendar


class TestCaselessdict(unittest.TestCase):
    def test_caselessdict_canonsort_keys(self) -> None:
        canonsort_keys = icalendar.caselessdict.canonsort_keys

        keys = ["DTEND", "DTSTAMP", "DTSTART", "UID", "SUMMARY", "LOCATION"]

        out = canonsort_keys(keys)
        assert out == ["DTEND", "DTSTAMP", "DTSTART", "LOCATION", "SUMMARY", "UID"]

        out = canonsort_keys(
            keys,
            (
                "SUMMARY",
                "DTSTART",
                "DTEND",
            ),
        )
        assert out == ["SUMMARY", "DTSTART", "DTEND", "DTSTAMP", "LOCATION", "UID"]

        out = canonsort_keys(
            keys,
            (
                "UID",
                "DTSTART",
                "DTEND",
            ),
        )
        assert out == ["UID", "DTSTART", "DTEND", "DTSTAMP", "LOCATION", "SUMMARY"]

        out = canonsort_keys(keys, ("UID", "DTSTART", "DTEND", "RRULE", "EXDATE"))
        assert out == ["UID", "DTSTART", "DTEND", "DTSTAMP", "LOCATION", "SUMMARY"]

    def test_caselessdict_canonsort_items(self) -> None:
        canonsort_items = icalendar.caselessdict.canonsort_items

        d = {
            "i": 7,
            "c": "at",
            "a": 3.5,
            "l": (2, 3),
            "e": [4, 5],
            "n": 13,
            "d": {"x": "y"},
            "r": 1.0,
        }

        out = canonsort_items(d)
        assert out == [
            ("a", 3.5),
            ("c", "at"),
            ("d", {"x": "y"}),
            ("e", [4, 5]),
            ("i", 7),
            ("l", (2, 3)),
            ("n", 13),
            ("r", 1.0),
        ]

        out = canonsort_items(d, ("i", "c", "a"))
        assert out, [
            ("i", 7),
            ("c", "at"),
            ("a", 3.5),
            ("d", {"x": "y"}),
            ("e", [4, 5]),
            ("l", (2, 3)),
            ("n", 13),
            ("r", 1.0),
        ]

    def test_caselessdict_copy(self) -> None:
        CaselessDict = icalendar.caselessdict.CaselessDict

        original_dict = CaselessDict(key1="val1", key2="val2")
        copied_dict = original_dict.copy()

        assert original_dict == copied_dict

    def test_CaselessDict(self) -> None:
        CaselessDict = icalendar.caselessdict.CaselessDict

        ncd = CaselessDict(key1="val1", key2="val2")
        assert ncd == CaselessDict({"KEY2": "val2", "KEY1": "val1"})

        assert ncd["key1"] == "val1"
        assert ncd["KEY1"] == "val1"

        assert ncd.has_key("key1")

        ncd["KEY3"] = "val3"
        assert ncd["key3"] == "val3"

        assert ncd.setdefault("key3", "FOUND") == "val3"
        assert ncd.setdefault("key4", "NOT FOUND") == "NOT FOUND"
        assert ncd["key4"] == "NOT FOUND"
        assert ncd.get("key1") == "val1"
        assert ncd.get("key3", "NOT FOUND") == "val3"
        assert ncd.get("key4", "NOT FOUND") == "NOT FOUND"
        assert "key4" in ncd

        del ncd["key4"]
        assert "key4" not in ncd

        ncd.update({"key5": "val5", "KEY6": "val6", "KEY5": "val7"})
        assert ncd["key6"] == "val6"

        keys = sorted(ncd.keys())
        assert keys == ["KEY1", "KEY2", "KEY3", "KEY5", "KEY6"]

    def test_eq_with_non_dict_types(self) -> None:
        """Test that CaselessDict.__eq__ handles non-dict comparisons correctly."""
        CaselessDict = icalendar.caselessdict.CaselessDict

        d = CaselessDict()
        d["test"] = 1

        # Should return False for non-dict types, not crash
        assert d != "string"
        assert d != 123
        assert d is not None
        assert d != []
        assert d != ()
        assert d != set()

        # Should still work correctly with dicts
        assert d == {"TEST": 1}
        assert d != {"TEST": 2}
        assert d != {"OTHER": 1}

    def test_ne_with_non_dict_types(self) -> None:
        """Test that CaselessDict.__ne__ handles non-dict comparisons correctly."""
        CaselessDict = icalendar.caselessdict.CaselessDict

        d = CaselessDict()
        d["test"] = 1

        # Should return True for non-dict types
        assert d != "string"
        assert d != 123
        assert d is not None
        assert d != []

        # Should still work correctly with dicts
        assert d == {"TEST": 1}
        assert d != {"TEST": 2}
    def test_non_string_key_raises_clean_typeerror(self) -> None:
        """CaselessDict keys must be str or bytes. A non-string key used to
        crash deep inside ``to_unicode(key).upper()`` with an opaque
        ``AttributeError: 'int' object has no attribute 'upper'``. The fix
        surfaces a clear ``TypeError`` naming the offending key and its
        type at the call site instead.

        Only hashable non-str/bytes values are tested here: an unhashable
        key like ``[1]`` is already rejected by ``dict()`` with a clear
        ``TypeError: unhashable type: 'list'`` and never reaches the
        CaselessDict-specific validation path.
        """
        CaselessDict = icalendar.caselessdict.CaselessDict
        for bad in (1, 1.5, None, object(), True, frozenset()):
            with self.assertRaises(TypeError) as ctx:
                CaselessDict({bad: "value"})
            msg = str(ctx.exception)
            assert "str or bytes" in msg, msg
            assert type(bad).__name__ in msg, msg

    def test_bytes_key_is_accepted(self) -> None:
        """Bytes keys are part of the documented contract and must continue
        to be accepted (used internally for cases like encoded property
        names coming from a binary source).
        """
        CaselessDict = icalendar.caselessdict.CaselessDict
        d = CaselessDict({b"summary": "Meeting"})
        assert d["SUMMARY"] == "Meeting"
        assert d["summary"] == "Meeting"

    def test_mixed_case_string_keys_normalized_at_construction(self) -> None:
        """The existing upper-case normalization must still run; the new
        type check is additive and must not break the documented contract
        of treating ``CaselessDict({"summary": 1, "SUMMARY": 2})`` as a
        single ``SUMMARY -> 2`` entry (last-wins, which is the same rule
        the upstream dict already applies to identical keys).
        """
        CaselessDict = icalendar.caselessdict.CaselessDict
        d = CaselessDict({"summary": 1, "SUMMARY": 2})
        assert list(d.keys()) == ["SUMMARY"]
        assert d["SUMMARY"] == 2

    def test_generator_arg_not_exhausted_by_init(self) -> None:
        """CaselessDict.__init__ must materialise a generator-style iterable
        before validating keys. The icalendar parser passes
        ``Parameters(...)`` with a generator of (key, value) pairs from
        ``Contentline.parts()``; if the validation loop iterates the
        generator, the subsequent ``super().__init__(*args, **kwargs)``
        receives an exhausted generator and the dict comes out empty.
        A previous version of this fix consumed the generator and
        silently dropped every parameter, which broke RDATE/TZID
        round-trips on real calendars.
        """
        CaselessDict = icalendar.caselessdict.CaselessDict
        # Mimic the generator the icalendar parser passes: an iterator
        # of (key, value) pairs that is consumed by ``dict()`` and that
        # ``CaselessDict`` must NOT touch until it is passed to
        # ``super().__init__``.
        def gen():
            yield ("key1", "val1")
            yield ("key2", "val2")
        d = CaselessDict(gen())
        assert d["KEY1"] == "val1"
        assert d["KEY2"] == "val2"
