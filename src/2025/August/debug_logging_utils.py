import inspect

import wrapt


def log(_func=None, *, prefix=None, propagate_exceptions=True, print_return_value=True):  # noqa: C901

    def format_args(args, kwargs):
        args_str = ", ".join(map(str, args)) if args else ""
        kwargs_str = ", ".join(f"{k}={v}" for k, v in kwargs.items()) if kwargs else ""
        return f"{args_str}{', ' if args_str and kwargs_str else ''}{kwargs_str}"

    @wrapt.decorator(enabled=True)
    async def async_wrapper(wrapped, instance, args, kwargs):
        print(
            f"\n[{prefix}]: {wrapped.__name__}({format_args(args, kwargs)})"
            if prefix
            else f"\n{wrapped.__name__}({format_args(args, kwargs)})"
        )
        try:
            result = await wrapped(*args, **kwargs)
            if print_return_value:
                print(f"Returned value:\n\t{result}")
            return result
        except Exception as e:
            print(f"Exception raised:\n {e}")
            if propagate_exceptions:
                raise
            return None

    @wrapt.decorator(enabled=True)
    def sync_wrapper(wrapped, instance, args, kwargs):
        print(
            f"\n[{prefix}]: {wrapped.__name__}({format_args(args, kwargs)})"
            if prefix
            else f"\n{wrapped.__name__}({format_args(args, kwargs)})"
        )
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

    def choose_wrapper(func):
        if inspect.iscoroutinefunction(func):
            return async_wrapper(func)
        return sync_wrapper(func)

    return choose_wrapper(_func) if callable(_func) else lambda f: choose_wrapper(f)


def class_debugger(_cls=None, *, hook=log):
    def decorator(_cls):
        for key, value in _cls.__dict__.items():
            if callable(value):
                setattr(_cls, key, hook(value))
        return _cls

    if callable(_cls):
        return decorator(_cls)

    return decorator
