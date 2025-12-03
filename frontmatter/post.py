from __future__ import (
    annotations,
)  # makes annotations strings automatically, so forward referencing works (?)
from typing import Any, Iterable
# from .default_handlers import BaseHandler  # this creates a circular import

__all__ = ["Post"]


class Post(object):
    """
    A Post contains content and metadata from frontmatter. This is what gets returned
    from `load <frontmatter.load>` and `loads <frontmatter.loads>`. Passing a Post to
    `dump <frontmatter.dump>` or `dumps <frontmatter.dumps>` turns the Post back to text.

    Has useful dundermethods (also see examples in comments)
    >>> post = frontmatter.load("./foo.txt")
    >>> title = post["title"]
    >>> tags = post["tags"]
    >>> # set a new key/value
    >>> post["foo"] = "bar"
    >>> print(frontmatter.dumps(post))
    """

    def __init__(
        self,
        content: str,
        handler: Any
        | None = None,  # using Any instead of BaseHandler to deal with circular dependency issue
        **metadata: object,
    ) -> None:  # I'm not sure it makes sense to have a return value here?
        self.content = str(content)
        self.metadata = metadata
        self.handler = handler

    def __getitem__(self, name: str) -> object:
        return self.metadata[name]  # e.g. post["title"]

    def __contains__(self, item: object) -> bool:
        return item in self.metadata  # e.g. "foo" in post

    def __setitem__(self, name: str, value: object) -> None:
        self.metadata[name] = value  # e.g. post["foo"] = "bar"

    def __delitem__(self, name: str) -> None:
        del self.metadata[name]  # e.g. del post["foo"]

    def __bytes__(self) -> bytes:
        # Convert string representation to bytes using utf-8 encoding
        return self.content.encode("utf-8")  # e.g bytes_representation = bytes(post)

    def __str__(self) -> str:
        return self.content  # e.g. print(post)  # returns content, not metadata

    def get(self, key: str, default: object = None) -> object:
        return self.metadata.get(key, default)  # e.g. post.get("title")

    def keys(self) -> Iterable[str]:
        # returns keys
        return self.metadata.keys()

    def values(self) -> Iterable[object]:
        # returns key values
        return self.metadata.values()

    def to_dict(self) -> dict[str, object]:
        # returns Post as a dict
        d = self.metadata.copy()
        d["content"] = self.content
        return d
