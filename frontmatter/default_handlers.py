"""
This module includes the handlers for YAML and TOML and a BaseHandler that outlines
the API.

A handler needs to do four things:
- detect if it can parse the text
- split the frontmatter from the content, returning both as a tuple
- parse the frontmatter into a dictionary
- export a dictionary back into text
"""

# To deal with forward referencing, but I'm not sure I've got this sorted out
# the __future__ import postpones the evaluation of type annotations in a module until
# runtime. The conflict is that Post uses the BaseHandler type and BaseHandler uses the Post type
from __future__ import annotations

import re
import tomllib as toml  # tomllib is in the Python standard library as of 3.11
import tomli_w  # used because tomllib doesn't have a dump method
import yaml
from .util import u
from .post import Post

from typing import Any, Type

# For my case this could probably be simplified to
# from yaml import CSafeDumper as SafeDumper
# from yaml import CSafeLoader as SafeLoader
# The try block could be removed.
SafeDumper: Type[yaml.CDumper] | Type[yaml.SafeDumper]
SafeLoader: Type[yaml.CSafeLoader] | Type[yaml.SafeLoader]

# Handle the case of PyYAML having been installed without C extensions
try:
    from yaml import CSafeDumper as SafeDumper
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeDumper
    from yaml import SafeLoader

__all__ = ["BaseHandler", "YAMLHandler", "TOMLHandler"]


DEFAULT_POST_TEMPLATE = """\
{start_delimiter}
{metadata}
{end_delimiter}

{content}
"""


class BaseHandler:
    FM_BOUNDARY: re.Pattern[str] | None = (
        None  # the type is the re | None union; the default is the = None part
    )
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
        """
        Detect if the handler can parse the given text.
        """
        assert self.FM_BOUNDARY is not None
        if self.FM_BOUNDARY.match(text):
            return True
        return False

    def split(self, text: str) -> tuple[str, str]:
        """
        Split text into frontmatter and content.
        """
        assert self.FM_BOUNDARY is not None
        _, fm, content = self.FM_BOUNDARY.split(text, 2)
        return fm, content

    def load(self, fm: str) -> dict[str, Any]:
        """
        Parse frontmatter and return a dict.
        """
        raise NotImplementedError

    def export(self, metadata: dict[str, object], **kwargs: object) -> str:
        """
        Turn metadata back into text.
        """
        raise NotImplementedError

    def format(self, post: Post, **kwargs: object) -> str:
        """
        Turn a post into a string, used in `frontmatter.dumps`.
        """
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
    """
    Load and export YAML metadata.
    """

    FM_BOUNDARY = re.compile(r"^-{3,}\s*$", re.MULTILINE)
    START_DELIMITER = END_DELIMITER = "---"

    def load(self, fm: str, **kwargs: object) -> Any:
        """
        Parse YAML frontmatter.
        """
        kwargs.setdefault("Loader", SafeLoader)
        return yaml.load(fm, **kwargs)  # type: ignore[arg-type]

    def export(self, metadata: dict[str, object], **kwargs: object) -> str:
        """
        Export metadata as YAML.
        """
        kwargs.setdefault("Dumper", SafeDumper)
        kwargs.setdefault("default_flow_style", False)
        kwargs.setdefault("allow_unicode", True)

        metadata_str = yaml.dump(metadata, **kwargs).strip()  # type: ignore[call-overload]
        return u(metadata_str)


class TOMLHandler(BaseHandler):  # pyright: ignore
    """
    Load and export TOML metadata.

    By default, the split is based on `+++`
    """

    FM_BOUNDARY = re.compile(r"^\+{3,}\s*$", re.MULTILINE)
    START_DELIMITER = END_DELIMITER = "+++"

    def load(self, fm: str, **kwargs: object) -> Any:
        assert toml is not None
        return toml.loads(fm, **kwargs)  # pyright: ignore

    def export(self, metadata: dict[str, object], **kwargs: object) -> str:
        "Turn metadata into TOML"
        assert toml is not None
        # Serialize Python data back into TOML. `tomllib` doesn't have a
        # `dumps` method, so...
        # This seems to be adding a newline at the end of the metadata
        metadata_str = tomli_w.dumps(metadata)
        print("TOML\n", metadata_str)
        return u(metadata_str)
