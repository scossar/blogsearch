import frontmatter
from frontmatter.default_handlers import TOMLHandler

post = frontmatter.load(
    "/home/scossar/projects/zalgorithm/content/notes/alchemy-restored.md",
    handler=TOMLHandler(),
)

print(post["title"])
print(post["tags"])
print(post.keys())
