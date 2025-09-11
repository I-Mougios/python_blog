import importlib

import pytest

dispatch_module = importlib.import_module("src.2025.07_July.dispatch")
Dispatcher = dispatch_module.Dispatcher

# ----- Fixtures -----


@pytest.fixture(scope="session")
def unregistered_key():
    class UnregisteredKey(KeyError):
        """Error to be raised when an unregistered key is requested"""

    return UnregisteredKey


@pytest.fixture(scope="function")
def simple_key_dispatcher(unregistered_key):
    error = unregistered_key("Not a registered key")

    @Dispatcher
    def dispatch_by_key(value1, value2="N/A", value3=None):
        """Raise error if key not found in registry"""
        raise error

    @dispatch_by_key.register("a")
    def _(value1, value2=None, value3=None):
        return value1

    @dispatch_by_key.register("b")
    def _(value1, value2="a", value3="b"):
        return value1

    return dispatch_by_key


@pytest.fixture(scope="function")
def type_based_dispatcher(unregistered_key):
    error = unregistered_key("Not a registered key")

    def fallback_fn(value1, value2, value3):
        raise error

    dispatcher = Dispatcher(fallback_fn, key_idx=1, key_generator=type)

    @dispatcher.register(str)
    def _(value1, value2, value3):
        return f"String value: {value2}"

    @dispatcher.register(int)
    def _(value1, value2, value3):
        return f"Integer value: {value2}"

    @dispatcher.register(list)
    def _(value1, value2, value3):
        return f"{type(value2).__name__} value: {value2}"

    return dispatcher


@pytest.fixture(scope="function")
def multi_arg_index_dispatcher(unregistered_key):
    error = unregistered_key("Not a registered key")

    def fallback_fn(value1, value2, value3):
        raise error

    dispatcher = Dispatcher(fallback_fn, key_idx=[0, 1])

    @dispatcher.register(("a", "b"))
    def _(value1, value2, value3):
        return f"Case1: {value1}-{value2}"

    @dispatcher.register(("c", "d"))
    def _(value1, value2, value3):
        return f"Case2: {value1}-{value2}"

    @dispatcher.register(("e", "f"))
    def _(value1, value2, value3):
        return f"Case3: {value1}-{value2}"

    return dispatcher


@pytest.fixture
def reversed_keyname_dispatcher(unregistered_key):
    def fallback_fn(*args, **kwargs):
        raise unregistered_key("Not a registered key")

    def reverse_keys(key1, key2):
        return key2, key1

    dispatcher = Dispatcher(fallback=fallback_fn, key_generator=reverse_keys, key_names=["key1", "key2"])

    @dispatcher.register(("b", "a"))
    def _(key1, key2):
        return f"Reversed order: {key1}, {key2}"

    @dispatcher.register(("", None))
    def _(key1, key2):
        return f"Empty values: key1={key1}, key2={key2}"

    return dispatcher


@pytest.fixture
def person_with_dispatcher(unregistered_key):
    def fallback_fn(*args, **kwargs):
        error = unregistered_key("Not a registered key")
        raise error

    class Person:
        def __init__(self, name):
            self.name = name

        # Dispatcher as a non-data descriptor
        talk = Dispatcher(fallback=fallback_fn, key_generator=None, key_idx=1)  # Skip 'self', dispatch on second arg

        @talk.register("Bob")
        def _(self, name):
            return f"{self.name} says hi to {name}"

        @talk.register("Alice")
        def _(self, name):
            return f"{self.name} says hi to {name}"

    return Person


# -------------- Tests --------------


def test_simple_key_dispatch(simple_key_dispatcher, unregistered_key):
    dispatcher = simple_key_dispatcher
    assert dispatcher.__name__ == "dispatch_by_key"
    assert dispatcher.__doc__ == "Raise error if key not found in registry"
    assert dispatcher("a") == "a"
    assert dispatcher("b") == "b"
    with pytest.raises(unregistered_key):
        dispatcher("c")


def test_type_based_dispatch(type_based_dispatcher, unregistered_key):
    dispatcher = type_based_dispatcher
    assert dispatcher("arg1", "hello", "arg3") == "String value: hello"
    assert dispatcher("arg1", 123, "arg3") == "Integer value: 123"
    assert dispatcher("arg1", [1, 2, 3], "arg3") == "list value: [1, 2, 3]"

    for t in (str, int, list):
        assert t in dispatcher.get_registry()

    with pytest.raises(TypeError):
        dispatcher.get_registry()[int] = "should fail"

    with pytest.raises(unregistered_key):
        dispatcher("x", {1, 2, 3}, None)

    # Register additional types mapped to the list handler
    list_handler = dispatcher.get_function(list)

    @dispatcher.register(set)
    @dispatcher.register(tuple)
    def _(value1, value2, value3):
        return list_handler(value1, value2, value3)

    assert dispatcher("x", {1, 2, 3}, None) == "set value: {1, 2, 3}"
    assert dispatcher("x", (1, 2, 3), None) == "tuple value: (1, 2, 3)"


def test_multi_arg_index_dispatch(multi_arg_index_dispatcher):
    dispatcher = multi_arg_index_dispatcher
    assert dispatcher("a", "b", "x") == "Case1: a-b"
    assert dispatcher("c", "d", "x") == "Case2: c-d"
    assert dispatcher("e", "f", "x") == "Case3: e-f"


def test_named_key_reversed_dispatch(reversed_keyname_dispatcher):
    dispatcher = reversed_keyname_dispatcher
    keys = dispatcher.get_registry().keys()

    assert dispatcher(key1="a", key2="b") == "Reversed order: a, b"
    assert dispatcher(key1=None, key2="") == "Empty values: key1=None, key2="

    assert ("", None) in keys

    with pytest.raises(TypeError) as exc:
        dispatcher("a", key2="b")
    assert "Missing required keyword arguments" in str(exc.value)


def test_dispatcher_as_class_method(person_with_dispatcher, unregistered_key):
    alice = person_with_dispatcher("Alice")
    bob = person_with_dispatcher("Bob")
    charlie = person_with_dispatcher("Charlie")

    assert alice.talk("Alice") == "Alice says hi to Alice"
    assert bob.talk("Bob") == "Bob says hi to Bob"

    with pytest.raises(unregistered_key):
        charlie.talk("Charlie")
