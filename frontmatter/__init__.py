"""
Frontmatter: Parse and manage posts with frontmatter

Based on python-frontmatter: https://github.com/eyeseast/python-frontmatter
Original code by Chris Amico, licensed under MIT

Alterations:
  - removes JSONHandler
  - requires the toml library and sets the TOMLHandler

"""

import io
import pathlib
from os import PathLike
from typing import Iterable, TextIO

from .default_handlers import TOMLHandler, YAMLHandler, BaseHandler
from .util import can_open, is_readable, is_writable, u
from .post import Post

__all__ = ["parse", "load", "loads", "dump", "dumps"]

# Calls the class constructor `Handler()` for each `Handler`
handlers = [Handler() for Handler in [YAMLHandler, TOMLHandler]]


def detect_format(text: str, handlers: Iterable[BaseHandler]) -> BaseHandler | None:
    for handler in handlers:
        if handler.detect(text):
            return handler
    return None


def parse(
    text: str,
    encoding: str = "utf-8",
    handler: BaseHandler | None = None,
    **defaults: object,
) -> tuple[dict[str, object], str]:
    text = u(text, encoding).strip()
    metadata = defaults.copy()
    handler = handler or detect_format(text, handlers)

    if handler is None:
        return metadata, text

    try:
        fm, content = handler.split(text)
    except ValueError:
        return metadata, text

    fm_data = handler.load(fm)
    if isinstance(fm_data, dict):
        metadata.update(fm_data)

    return metadata, content.strip()


def check(fd: TextIO | PathLike[str] | str, encoding: str = "utf-8") -> bool:
    if is_readable(fd):
        text = fd.read()

    elif can_open(fd):
        with open(fd, "r", encoding=encoding) as f:
            text = f.read()

    else:
        return False

    return checks(text, encoding)


def checks(text: str, encoding: str = "utf-8") -> bool:
    text = u(text, encoding)
    return detect_format(text, handlers) is not None


def load(
    fd: str | io.IOBase | pathlib.Path,
    encoding: str = "utf-8",
    handler: BaseHandler | None = None,
    **defaults: object,
) -> Post:
    if is_readable(fd):
        text = fd.read()
    elif can_open(fd):
        with open(fd, "r", encoding=encoding) as f:
            text = f.read()

    else:
        raise ValueError(f"Cannot open filename using type {type(fd)}")

    handler = handler or detect_format(text, handlers)
    return loads(text, encoding, handler, **defaults)


def loads(
    text: str,
    encoding: str = "utf-8",
    handler: BaseHandler | None = None,
    **defaults: object,
) -> Post:
    text = u(text, encoding)
    handler = handler or detect_format(text, handlers)
    metadata, content = parse(text, encoding, handler, **defaults)
    return Post(content, handler, **metadata)


def dump(
    post: Post,
    fd: str | PathLike[str] | TextIO,
    encoding: str = "utf-8",
    handler: BaseHandler | None = None,
    **kwargs: object,
) -> None:
    content = dumps(post, handler, **kwargs)
    if is_writable(fd):
        fd.write(content)
    elif can_open(fd):
        with open(fd, "w", encoding=encoding) as f:
            f.write(content)
    else:
        raise ValueError(f"Cannot open filename using type {type(fd)}")


def dumps(
    post: Post,
    handler: BaseHandler | None = None,
    **kwargs: object,
) -> str:
    if handler is None:
        handler = getattr(post, "handler", None) or YAMLHandler()

    assert handler is not None
    return handler.format(post, **kwargs)
