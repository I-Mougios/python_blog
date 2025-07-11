# dispatch.py
from types import MappingProxyType, MethodType
from typing import Any, Callable, Dict, List, Optional, Set, TypeVar, Union

__all__ = ["Dispatcher"]

T = TypeVar("T")


class Dispatcher:
    """
    A class to manage function dispatching based on the selected argument.
    By default, it performs the dispatching based on the first argument.

    Attributes:
        fallback (Callable): The default function to call if no mapping matches.

        registry (Dict[Any, Callable]): A dictionary mapping values to specific functiÎÎÎons.
    """

    def __init__(
        self,
        fallback: Callable[..., Any],
        key_idx: Optional[Union[int, List[int]]] = 0,
        key_generator: Optional[Callable] = None,
        key_names: Optional[Union[str, List[str], Set[str]]] = None,
    ):
        """
        Initialize the dispatcher with a default function.

        Args:
            fallback (Callable[..., Any]): The default function to call when no mapping is found.
            key_idx (int | List[int], optional): The index of the argument to be dispatched.
                If dispatching is done by index, the key must be passed as a positional argument.
            key_generator (Callable[[Any], Any], optional): A function applied to the selected argument for dispatching.
            key_names (str | List[str] | Set[str], optional): The names of the arguments to be used for dispatching.
                If named arguments are used instead of an index, the arguments used
                for dispatching must be passed as keyword arguments.
                By default, dispatching is performed using the first argument.
        """
        self.fallback = fallback
        self.registry: Dict[Any, Callable[..., Any]] = {}
        self.key_idx = key_idx
        self.key_generator = key_generator
        self.key_names = key_names
        self.__doc__ = fallback.__doc__
        self.__name__ = fallback.__name__

        # Coerce the key_names to set to facilitate some validation check when I extract the key
        if self.key_names:
            if isinstance(self.key_names, str):
                self.key_names = {self.key_names}
            elif isinstance(self.key_names, (tuple, list)):
                self.key_names = set(key_names)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """
        Dispatch to the appropriate function based on the selected argument.

        Args:
            *args: Positional arguments to pass to the selected function.
            **kwargs: Keyword arguments to pass to the selected function.

        Returns:
            The result of the dispatched function.
        """
        if not (args or kwargs):
            raise ValueError("At least one positional or keyword argument is required for dispatching.")

        key = self.extract_key(args, kwargs)
        function_to_call = self.registry.get(key, self.fallback)
        return function_to_call(*args, **kwargs)

    def __get__(self, instance, owner_class):
        if instance is None:
            return self

        return MethodType(self, instance)

    def register(self, key: Any) -> Callable[[Callable[..., T]], Callable[..., T]]:
        """
        Decorator factory to register a function to handle a specific key.

        Args:
            key (Any): The key to associate with the function.

        Returns:
            A decorator function that registers the provided function and return the same function as it is.
        """

        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            self.registry[key] = func
            return func

        return decorator

    def get_registry(self) -> MappingProxyType:
        """
        Get an immutable view of the current function registry.

        Returns:
            MappingProxyType: An immutable mapping of registered keys to functions.
        """
        return MappingProxyType(self.registry)

    def get_function(self, key: Any) -> Callable[..., T]:
        """
        Retrieve the function mapped to a specific key, or the default function.

        Args:
            key (Any): The key to look up.

        Returns:
            Callable[..., Any]: The function associated with the key, or the default function.
        """
        return self.registry.get(key, self.fallback)

    def extract_key(self, args, kwargs):
        if self.key_names:
            # Check if there is a key that is not in the kwargs
            missing_keys = self.key_names - kwargs.keys()
            if missing_keys:
                raise TypeError(
                    f"Missing required keyword arguments: {missing_keys}."
                    f" Arguments used for dispatching must be passed as keyword arguments."
                )
            # Create the dictionary with key-values to be passed to the key generator function
            kws = {key: kwargs[key] for key in self.key_names}

            if self.key_generator:
                return self.key_generator(**kws)
            else:
                return tuple(kws.values())
        else:
            if self.key_generator:
                return self.key_generator(args[self.key_idx])

            if isinstance(self.key_idx, (tuple, list)):
                return tuple((args[i] for i in self.key_idx))

            return args[self.key_idx]
