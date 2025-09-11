import weakref
from typing import Any, Generator


class DescriptorRegistry:
    """
    A registry for storing per-instance values associated with descriptor objects,
    using weak references to avoid memory leaks and support garbage collection.

    Motivation
    ----------
    In Python, implementing descriptors that store values on a per-instance basis
    can be tricky due to several pitfalls:

    1. **Shadowing and Recursion Hazards**:
        Descriptors that attempt to store their data on the instance using a name
        (e.g., `instance.__dict__["_" + self.name] = value`) may accidentally overwrite
        an existing attribute. The underscore is a convention for private attributes and in this implementation,
        is necessary in order to avoid infinite recursion
        in the __get__ method if it makes use of getattr(instance, key, default)

    2. **Lack of __dict__ in Slotted Classes**:
        Storing values in the instance’s `__dict__` is not always possible—
        particularly when the class uses `__slots__` and does not include `__dict__`
        or `__weakref__`. This makes direct instance storage brittle and error-prone.

    3. **Global State is Unsafe**:
        Using global registries or class-level attributes for storing per-instance
        values breaks encapsulation and may lead to memory leaks unless the values
        are garbage-collected properly.

    Design
    ------
    This class uses `id(instance)` as the key and stores a `weakref.ref(instance)`
    along with the value in an internal dictionary. When the instance is garbage collected,
    the weak reference callback automatically cleans up the associated data.

    This design provides:
    - Safe, indirect per-instance storage.
    - Compatibility with all classes that support weak references, including slotted classes
      with `__weakref__` declared.
    - Automatic memory cleanup upon object destruction.

    Interface
    ---------
    - `__setitem__`, `__getitem__`: Standard item access storing the value for an instance.
    - `get`, `keys`, `values`, `items`, `valuerefs`: Utilities to introspect or retrieve the
      current state of the registry.
    - `__contains__`: Checks if a given instance is currently in the registry.
    - `__repr__`: String representation useful for debugging.

    Limitations
    -----------
    This registry can only be used with objects that support weak referencing.
    If an object does not support weak references (e.g., slotted classes without `__weakref__`),
    inserting them will raise a `TypeError`.
    """

    def __init__(self):
        self._data = {}

    def __setitem__(self, key, value):
        obj_id = id(key)

        def remove(_):
            self._data.pop(obj_id, None)

        self._data[obj_id] = (weakref.ref(key, remove), value)

    def __getitem__(self, key: object) -> Any:
        weakref_value_tuple = self._data.get(id(key))
        if weakref_value_tuple is None:
            raise KeyError(f"{key} not found in storage")
        return weakref_value_tuple[1]

    def __contains__(self, key: object) -> bool:
        return id(key) in self._data

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._data})"

    def get(self, key: object, default: Any = None) -> Any:
        pair = self._data.get(id(key))
        return pair[1] if pair is not None else default

    def items(self) -> Generator[tuple[object, Any], None, None]:
        return ((ref(), value) for ref, value in self._data.values())

    def values(self) -> Generator[Any, None, None]:
        return (value for ref, value in self._data.values())

    def keys(self) -> Generator[object, None, None]:
        return (ref() for ref, _ in self._data.values())

    def valuerefs(self) -> Generator[weakref.ReferenceType]:
        return (ref for ref, _ in self._data.values())
