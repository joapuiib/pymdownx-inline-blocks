import re
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor


class InlineBlockPreprocessor(Preprocessor):
    # Match forms:
    # 1. /// block: content
    # 2. /// block | modifiers : content
    RE = re.compile(
        r'^(?P<indent>[ \t]*)'                      # Capture leading indentation
        r'(?P<slashes>/{3,})\s*'                   # Capture 3+ leading slashes
        r'(?P<block>[a-zA-Z0-9_-]+)'               # Block type
        r'(?:\s*\|\s*(?P<modifiers>[^:]+))?'       # Optional modifiers
        r'\s*:\s*'
        r'(?P<content>.+)$'                        # Content
    )

    def run(self, lines):
        new_lines = []
        for line in lines:
            m = self.RE.match(line)
            if m:
                indent = m.group("indent") or ""
                slashes = m.group("slashes")
                block_type = m.group("block")
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
    def extendMarkdown(self, md):
        md.preprocessors.register(
            InlineBlockPreprocessor(md),
            "inline_blocks",
            25,
        )


def makeExtension(*args, **kwargs):
    """Return extension."""

    return InlineBlockExtension(*args, **kwargs)
