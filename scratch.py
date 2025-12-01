import frontmatter
from frontmatter.default_handlers import TOMLHandler, YAMLHandler
from io import StringIO

post = frontmatter.load(
    "/home/scossar/projects/zalgorithm/content/notes/alchemy-restored.md"
)

print("title", post["title"])
print("tags", post["tags"])
print("keys", post.keys())
# f = StringIO()
# frontmatter.dump(post, f)
# print("dump", f.getvalue())
# print(frontmatter.dumps(post, handler=YAMLHandler()))
post["foo"] = "bar"
print("keys", post.keys())
print("contains foo", "foo" in post)
del post["foo"]
print("contains foo", "foo" in post)
# print("bytes", bytes(post))
# print("content", post)
print("get title", post.get("title"))
# print("post dict", post.to_dict())
print(frontmatter.dumps(post))
