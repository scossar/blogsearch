from __future__ import (
    annotations,
)  # makes annotations strings automatically, so forward referencing works
from typing import Iterable
from .default_handlers import BaseHandler

__all__ = ["Post"]


class Post(object):
    def __init__(
        self,
        content: str,
        handler: BaseHandler | None = None,
        **metadata: object,
    ) -> None:
        self.content = str(content)
        self.metadata = metadata
        self.handler = handler

    def __getitem__(self, name: str) -> object:
        return self.metadata[name]

    def __contains__(self, item: object) -> bool:
        return item in self.metadata

    def __setitem__(self, name: str, value: object) -> None:
        self.metadata[name] = value

    def __delitem__(self, name: str) -> None:
        del self.metadata[name]

    def __bytes__(self) -> bytes:
        return self.content.encode("utf-8")

    def __str__(self) -> str:
        return self.content

    def get(self, key: str, default: object = None) -> object:
        return self.metadata.get(key, default)

    def keys(self) -> Iterable[str]:
        return self.metadata.keys()

    def values(self) -> Iterable[object]:
        return self.metadata.values()

    def to_dict(self) -> dict[str, object]:
        d = self.metadata.copy()
        d["content"] = self.content
        return d
