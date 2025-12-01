from __future__ import annotations

import re
import yaml
from .util import u
from .post import Post

from typing import Any, Type, Iterable

SafeDumper: Type[yaml.CDumper] | Type[yaml.SafeDumper]
SafeLoader: Type[yaml.CSafeLoader] | Type[yaml.SafeLoader]

try:
    from yaml import CSafeDumper as SafeDumper
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeDumper
    from yaml import SafeLoader

try:
    import toml
except ImportError:
    toml = None

__all__ = ["BaseHandler", "YAMLHandler", "TOMLHandler"]


DEFAULT_POST_TEMPLATE = """\
{start_delimiter}
{metadata}
{end_delimiter}

{content}
"""


class BaseHandler:
    FM_BOUNDARY: re.Pattern[str] | None = None
    START_DELIMITER: str | None = None
    END_DELIMITER: str | None = None

    def __init__(
        self,
        fm_boundary: re.Pattern[str] | None = None,
        start_delimiter: str | None = None,
        end_delimiter: str | None = None,
    ):
        self.FM_BOUNDARY = fm_boundary or self.FM_BOUNDARY
        self.START_DELIMITER = start_delimiter or self.START_DELIMITER
        self.END_DELIMITER = end_delimiter or self.END_DELIMITER

        if self.FM_BOUNDARY is None:
            raise NotImplementedError(
                "No frontmatter boundary defined. "
                "Please set {}.FM_BOUNDARY to a regular expression".format(
                    self.__class__.__name__
                )
            )

    def detect(self, text: str) -> bool:
        assert self.FM_BOUNDARY is not None
        if self.FM_BOUNDARY.match(text):
            return True
        return False

    def split(self, text: str) -> tuple[str, str]:
        assert self.FM_BOUNDARY is not None
        _, fm, content = self.FM_BOUNDARY.split(text, 2)
        return fm, content

    def load(self, fm: str) -> dict[str, Any]:
        raise NotImplementedError

    def export(self, metadata: dict[str, object], **kwargs: object) -> str:
        raise NotImplementedError

    def format(self, post: Post, **kwargs: object) -> str:
        start_delimiter = kwargs.pop("start_delimiter", self.START_DELIMITER)
        end_delimiter = kwargs.pop("end_delimiter", self.END_DELIMITER)

        metadata = self.export(post.metadata, **kwargs)

        return DEFAULT_POST_TEMPLATE.format(
            metadata=metadata,
            content=post.content,
            start_delimiter=start_delimiter,
            end_delimiter=end_delimiter,
        ).strip()


class YAMLHandler(BaseHandler):
    FM_BOUNDARY = re.compile(r"^-{3,}\s*$", re.MULTILINE)
    START_DELIMITER = END_DELIMITER = "---"

    def load(self, fm: str, **kwargs: object) -> Any:
        kwargs.setdefault("Loader", SafeLoader)
        return yaml.load(fm, **kwargs)  # type: ignore[arg-type]

    def export(self, metadata: dict[str, object], **kwargs: object) -> str:
        kwargs.setdefault("Dumper", SafeDumper)
        kwargs.setdefault("default_flow_style", False)
        kwargs.setdefault("allow_unicode", True)

        metadata_str = yaml.dump(metadata, **kwargs).strip()  # type: ignore[call-overload]
        return u(metadata_str)


class TOMLHandler(BaseHandler):  # pyright: ignore
    FM_BOUNDARY = re.compile(r"^\+{3,}\s*$", re.MULTILINE)
    START_DELIMITER = END_DELIMITER = "+++"

    def load(self, fm: str, **kwargs: object) -> Any:
        assert toml is not None
        return toml.loads(fm, **kwargs)  # pyright: ignore

    def export(self, metadata: dict[str, object], **kwargs: object) -> str:
        assert toml is not None
        metadata_str = toml.dumps(metadata)
        return u(metadata_str)
