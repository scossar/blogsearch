import frontmatter
from frontmatter import Post
from pathlib import Path
from typing import cast, Any, Dict, List
import re
import mistune

postspath = "/home/scossar/projects/zalgorithm/content"
# To generate an AST, call with `markdown(post.content)`
# See https://github.com/lepture/mistune/blob/4adac1c6e7e14e7deeb1bf6c6cd8c6816f537691/docs/renderers.rst#L56
# for the list of available methods (list of nodes that will be generated)
markdown = mistune.create_markdown(
    renderer=None, plugins=["footnotes"]
)  # Creates an AST renderer


def should_process_file(filepath: Path) -> bool:
    if any(part.startswith(".") for part in filepath.parts):
        print("starts with .")
        return False
    if filepath.suffix.lower() not in (".md", ".markdown"):
        return False
    return True


def load_file(filepath: Path) -> Post:
    post = frontmatter.load(filepath)
    return post


def post_chunks(content: str) -> List[str]:
    chunks = re.split(r"\n(?=#)", content)
    return chunks


def extract_text_from_node(node: Dict[str, Any]) -> str:
    if node["type"] == "text":
        return node["raw"]

    # this will remove the footnotes section, as long as it's properly structured
    if node["type"] == "footnote_item":
        return ""

    if node["type"] == "block_code":
        lang = node["attrs"].get("info", "")
        code = node["raw"]
        if lang:
            return f"\n\nCode ({lang}):\n{code}\n\n"
        return f"\n\nCode:\n{code}\n\n"

    if (
        node["type"] == "softbreak"
        or node["type"] == "linebreak"
        or node["type"] == "blank_line"
    ):
        return " "

    # a list is made up of list_items that contain block_text nodes
    if node["type"] == "list":
        items_text = extract_text(node["children"])
        return f"\n{items_text}\n"

    # list items
    if node["type"] == "list_item":
        item_text = extract_text(node["children"])
        return f"- {item_text}\n"

    # list_item text
    if node["type"] == "block_text":
        return extract_text(node["children"])

    if node["type"] == "paragraph":
        text = extract_text(node["children"])
        return text + "\n\n"

    if "children" in node:
        return extract_text(node["children"])

    return ""


def extract_text(nodes: List[Dict[str, Any]]) -> str:
    return "".join(extract_text_from_node(node) for node in nodes)


def extract_sections(
    ast: List[Dict[str, Any]], headings: List[str] = []
) -> List[Dict[str, str]]:
    sections = []
    current_section = {"headings": headings.copy(), "content": []}

    for node in ast:
        if node["type"] == "heading":
            if current_section["content"]:
                sections.append(current_section)

            # new section
            heading_text = extract_text(node["children"])
            level = node["attrs"]["level"]

            headings = headings[: level - 1] + [heading_text]
            current_section = {"headings": headings, "content": []}

        else:
            text = extract_text_from_node(node)
            text = re.sub(r"\[\^\d+\]", "", text)  # remove footnote refs from text
            if text.strip():
                current_section["content"].append(text)

    if current_section["content"]:
        sections.append(current_section)

    return sections


for path in Path(postspath).rglob("*"):
    if not should_process_file(path):
        continue
    stem = path.stem
    # testing
    # stem_name = "chunking_hugo_post_content_for_semantic_search"
    stem_name = "roger-bacon-as-magician"
    if stem == stem_name:
        post = load_file(path)
        title = str(post["title"])  # it's a string
        nodes = markdown(post.content)
        nodes = cast(list[dict[str, Any]], nodes)
        # From `markdown.py`, the __call__(self, s: str) method calls `self.parse(s)[0]`
        # The return type is `Union[str, List[Dict[str, Any]]]`, but for the "None" renderer
        # the returned type will be `List[Dict[str, Any]]`
        # for node in nodes[:25]:
        #     print(node)
        #     print("\n")
        sections = extract_sections(nodes, headings=[title])
        for section in sections:
            print(section)
            print("\n")
