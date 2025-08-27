import inspect
import json
import logging
import logging.config
import re
from datetime import UTC, datetime
from pathlib import Path

import wrapt
from icecream import ic
from yaml import safe_load


def configure_loggers(directory: str | None = None, filename: str = "logger_config.yaml") -> dict | None:
    try:
        parents = Path(__file__).resolve().parents
    except NameError:
        parents = ic(Path.cwd().resolve().parents)

    for path in parents:
        if directory is not None:
            path = path / directory

        candidate = path / filename

        if candidate.exists():
            with open(candidate, encoding="utf-8") as f:
                config = safe_load(f)

            logging.config.dictConfig(config)
            return config

    raise FileNotFoundError(f"{filename} not found")


class SQLAlchemyFormatter(logging.Formatter):

    @staticmethod
    def _extract_query_from_exception(exc_value: str) -> dict:

        exc_str = str(exc_value)
        sql_match = re.search(r"\[SQL:\s*(.*?)\]", exc_str, re.DOTALL)
        params_match = re.search(r"\[parameters:\s*(.*?)\]", exc_str, re.DOTALL)
        return {"query": sql_match.group(1), "params": params_match.group(1)}

    def format(self, record: logging.LogRecord) -> str:  # noqa A003
        if record.exc_info:
            # Get the exception components
            exc_type, exc_value, exc_traceback = record.exc_info
            exception = {"exc_type": exc_type.__name__, "exc_summary": str(exc_value).split("\n")[0]}

            query_dict = self._extract_query_from_exception(exc_value)
            exception.update(query_dict)
            exception_json = json.dumps(exception, indent=2)
            return exception_json

        return record.getMessage()


class SQLAlchemyFilter(logging.Filter):
    SQL_KEYWORDS = ("SELECT", "INSERT", "UPDATE", "CREATE", "DELETE", "ALTER")

    def filter(self, record: logging.LogRecord) -> bool:  # noqa A003
        # Always keep logs with exceptions
        if record.exc_info:
            return True

        # Normalize message to uppercase for comparison
        msg = record.getMessage().strip().upper()

        if msg.startswith(self.SQL_KEYWORDS):
            return True

        return False


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord):  # noqa A003
        log_dict = {
            "created": self.serialize_local_timestamp(record.created),
            "msec": record.msecs,
            "loggerName": record.name,
            "module": record.module,
            "lineno": record.lineno,
            "message": record.getMessage(),
            "exceptionInfo": (self.formatException(record.exc_info) if record.exc_info else None),
            "stackTrace": (self.formatStack(record.stack_info) if record.stack_info else None),
        }

        return json.dumps(log_dict, indent=2)

    @staticmethod
    def serialize_local_timestamp(t: float) -> str:
        dt = datetime.fromtimestamp(t, UTC)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


class CustomFilter(logging.Filter):
    def __init__(self, **kwargs):
        super().__init__()
        self.extra = kwargs

    def filter(self, record: logging.LogRecord):  # noqa A003
        include = getattr(record, "include", True)
        return bool(include)


def log(_func=None, *, prefix=None, propagate_exceptions=True, print_return_value=True):  # noqa: C901

    def format_args(args, kwargs):
        args_str = ", ".join(map(str, args)) if args else ""
        kwargs_str = ", ".join(f"{k}={v}" for k, v in kwargs.items()) if kwargs else ""
        return f"{args_str}{', ' if args_str and kwargs_str else ''}{kwargs_str}"

    @wrapt.decorator(enabled=True)
    async def async_wrapper(wrapped, instance, args, kwargs):
        print(  # noqa  T201
            f"\n[{prefix}]: {wrapped.__name__}({format_args(args, kwargs)})"
            if prefix
            else f"\n{wrapped.__name__}({format_args(args, kwargs)})"
        )
        try:
            result = await wrapped(*args, **kwargs)
            if print_return_value:
                print(f"Returned value:\n\t{result}")  # noqa  T201
            return result
        except Exception as e:
            print(f"Exception raised:\n {e}")  # noqa  T201
            if propagate_exceptions:
                raise
            return None

    @wrapt.decorator(enabled=True)
    def sync_wrapper(wrapped, instance, args, kwargs):
        print(  # noqa  T201
            f"\n[{prefix}]: {wrapped.__name__}({format_args(args, kwargs)})"
            if prefix
            else f"\n{wrapped.__name__}({format_args(args, kwargs)})"
        )
        try:
            result = wrapped(*args, **kwargs)
            if print_return_value:
                print(f"Returned value:\n\t{result}")  # noqa  T201
            return result
        except Exception as e:
            print(f"Exception raised:\n {e}")  # noqa  T201
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
