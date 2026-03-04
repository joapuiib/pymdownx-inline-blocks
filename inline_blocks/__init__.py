import re
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor


class InlineBlockPreprocessor(Preprocessor):
    # Match forms:
    # 1. /// block: content
    # 2. /// block | modifiers : content
    # 3. ///<delim> block | modifiers <delim> content
    HEADER_RE = re.compile(
        r'^(?P<indent>[ \t]*)'                     # Leading indentation
        r'(?P<slashes>/{3,})'                      # 3+ leading slashes
        r'(?P<delimiter>\S)?'                      # Optional delimiter (non-whitespace)
        r'\s*'                                     # Optional whitespace
        r'(?P<block>[a-zA-Z0-9_-]+)'               # Block type
        r'(?P<header>.+)$'                         # optional modifiers + content
    )

    def __init__(self, md, exclude_blocks=[], delimiter=":", block_delimiter={}):
        super().__init__(md)
        self.exclude_blocks = exclude_blocks
        self.delimiter = delimiter
        self.block_delimiter = block_delimiter

    def run(self, lines):
        new_lines = []
        for line in lines:
            m = self.HEADER_RE.match(line)
            if m:
                indent = m.group("indent") or ""
                slashes = m.group("slashes")
                block = m.group("block").strip()
                delimiter = m.group("delimiter") or self.block_delimiter.get(block, self.delimiter)
                header = m.group("header").strip()

                if block in self.exclude_blocks:
                    new_lines.append(line)
                    continue

                if delimiter not in header:
                    new_lines.append(line)
                    continue

                before, content = map(str.strip, header.split(delimiter, 1))

                modifiers = None
                if "|" in before:
                    _, modifiers = map(str.strip, before.split("|", 1))

                if modifiers:
                    new_lines.append(f"{indent}{slashes} {block} | {modifiers.strip()}")
                else:
                    new_lines.append(f"{indent}{slashes} {block}")

                if content:
                    new_lines.append(f"{indent}{content}")
                new_lines.append(f"{indent}{slashes}")
            else:
                new_lines.append(line)
        return new_lines


class InlineBlockExtension(Extension):
    def __init__(self, **kwargs):
        self.config = {
            "exclude_blocks": [["html"], "List of block types to exclude from processing"],
            "delimiter": [":", "Delimiter separating block type from content (default ':')"],
            "block_delimiter": [{}, "Dictionary for specifying a default delimeter for specific block types"],
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        md.preprocessors.register(
            InlineBlockPreprocessor(
                md,
                exclude_blocks=self.getConfig("exclude_blocks"),
                delimiter=self.getConfig("delimiter"),
                block_delimiter=self.getConfig("block_delimiter"),
            ),
            "inline_blocks",
            25,
        )


def makeExtension(**kwargs):
    return InlineBlockExtension(**kwargs)

