import wrapt


def log(_func=None, *, prefix=None, propagate_exceptions=True, print_return_value=True):

    @wrapt.decorator(enabled=True)
    def wrapper(wrapped, instance, args, kwargs):
        # Convert positional arguments to strings and join them with commas
        args_str = ", ".join(map(str, args)) if args else ""
        # Convert keyword arguments to "key=value" format and join with commas
        kwargs_str = ", ".join(f"{k}={v}" for k, v in kwargs.items()) if kwargs else ""
        if prefix is not None:
            print(f"\n[{prefix}]: {wrapped.__name__}({args_str}{kwargs_str})\n")
        else:
            print(f"\n{wrapped.__name__}({args_str}{kwargs_str})\n")
        try:
            result = wrapped(*args, **kwargs)

            if print_return_value:
                print(f"Returned value:\n\t{result}")
            return result
        except Exception as e:
            print(f"Exception raised:\n {e}")
            if propagate_exceptions:
                raise
            return None

    if callable(_func):
        return wrapper(_func)

    return wrapper


def class_debugger(_cls=None, *, hook=log):
    def decorator(_cls):
        for key, value in _cls.__dict__.items():
            if callable(value):
                setattr(_cls, key, hook(value))
        return _cls

    if callable(_cls):
        return decorator(_cls)

    return decorator
