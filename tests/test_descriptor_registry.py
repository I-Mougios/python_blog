import importlib
import weakref

import pytest

DescriptorRegistry = importlib.import_module("src.2025.August.descriptor_registry").DescriptorRegistry


# --- Test Fixtures ---


class NoSlots:
    def __init__(self, name):
        self.name = name


class SlotsNoWeakref:
    __slots__ = ("name",)

    def __init__(self, name):
        self.name = name


class SlotsWithWeakref:
    __slots__ = ("name", "__weakref__")

    def __init__(self, name):
        self.name = name


# --- Test Class ---


class TestDescriptorRegistry:

    def setup_method(self):
        self.registry = DescriptorRegistry()

    def test_set_and_getitem_with_normal_class(self):
        obj = NoSlots("A")
        self.registry[obj] = "value"
        assert self.registry[obj] == "value"

    def test_setitem_raises_typeerror_for_slots_no_weakref(self):
        obj = SlotsNoWeakref("B")
        with pytest.raises(TypeError, match="cannot create weak reference to 'SlotsNoWeakref' object"):
            self.registry[obj] = "value"

    def test_set_and_getitem_with_slots_with_weakref(self):
        obj = SlotsWithWeakref("C")
        self.registry[obj] = "value"
        assert self.registry[obj] == "value"

    def test_contains(self):
        obj = NoSlots("D")
        assert obj not in self.registry
        self.registry[obj] = "val"
        assert obj in self.registry

    def test_get_with_default(self):
        obj = NoSlots("E")
        assert self.registry.get(obj, "default") == "default"
        self.registry[obj] = "real"
        assert self.registry.get(obj) == "real"

    def test_items_keys_values(self):
        a = NoSlots("A")
        b = NoSlots("B")
        self.registry[a] = "1"
        self.registry[b] = "2"

        keys = list(self.registry.keys())
        values = list(self.registry.values())
        items = list(self.registry.items())

        assert a in keys and b in keys
        assert "1" in values and "2" in values
        assert (a, "1") in items
        assert (b, "2") in items

    def test_valuerefs(self):
        a = NoSlots("A")
        self.registry[a] = "val"
        refs = list(self.registry.valuerefs())
        assert isinstance(refs[0], weakref.ReferenceType)
        assert refs[0]() is a

    def test_repr(self):
        obj = NoSlots("A")
        self.registry[obj] = "x"
        assert "DescriptorRegistry" in repr(self.registry)

    def test_cleanup_on_object_deletion(self):
        obj = NoSlots("temp")
        self.registry[obj] = "z"
        key_id = id(obj)
        assert key_id in self.registry._data

        # Delete reference
        del obj
        assert key_id not in self.registry._data
