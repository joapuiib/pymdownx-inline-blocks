import re
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor


class InlineBlockPreprocessor(Preprocessor):
    # Match forms:
    # 1. /// block: content
    # 2. /// block | modifiers : content
    RE = re.compile(
        r'^(?P<indent>[ \t]*)'                     # Capture leading indentation
        r'(?P<slashes>/{3,})\s*'                   # Capture 3+ leading slashes
        r'(?P<block>[a-zA-Z0-9_-]+)'               # Block type
        r'(?:\s*\|\s*(?P<modifiers>[^:]+))?'       # Optional modifiers
        r'\s*:\s*'
        r'(?P<content>.+)$'                        # Content
    )

    def __init__(self, md, exclude_blocks=[]):
        super().__init__(md)
        self.exclude_blocks = exclude_blocks

    def run(self, lines):
        new_lines = []
        for line in lines:
            m = self.RE.match(line)
            if m:
                block_type = m.group("block")
                if block_type in self.exclude_blocks:
                    new_lines.append(line)
                    continue

                indent = m.group("indent") or ""
                slashes = m.group("slashes")
                modifiers = m.group("modifiers")
                content = m.group("content").strip()

                if modifiers:
                    new_lines.append(f"{indent}{slashes} {block_type} | {modifiers.strip()}")
                else:
                    new_lines.append(f"{indent}{slashes} {block_type}")
                new_lines.append(f"{indent}{content}")
                new_lines.append(f"{indent}{slashes}")
            else:
                new_lines.append(line)
        return new_lines


class InlineBlockExtension(Extension):
    def __init__(self, **kwargs):
        self.config = {
            "exclude_blocks": [["html"], "List of block types to exclude from processing"]
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        md.preprocessors.register(
            InlineBlockPreprocessor(md, self.getConfig("exclude_blocks")),
            "inline_blocks",
            25,
        )


def makeExtension(**kwargs):
    return InlineBlockExtension(**kwargs)

