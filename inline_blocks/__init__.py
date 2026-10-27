import re
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor


class InlineBlockPreprocessor(Preprocessor):
    # Match forms:
    # 1. /// block: content
    # 2. /// block | modifiers : content
    # 3. ///<delim> block | modifiers <delim> content
    #    (<delim> must be followed by whitespace, so "///block" is "/// block")
    HEADER_RE = re.compile(
        r'^(?P<indent>[ \t]*)'                     # Leading indentation
        r'(?P<slashes>/{3,})'                      # 3+ leading slashes
        r'(?:(?P<delimiter>\S)\s+|\s*)'            # Optional delimiter followed by whitespace
        r'(?P<block>[a-zA-Z0-9_-]+)'               # Block type
        r'(?P<header>.*)$'                         # optional modifiers + content
    )

    def __init__(self, md, exclude_blocks=None, delimiter=":", block_delimiter=None):
        super().__init__(md)
        self.exclude_blocks = exclude_blocks or []
        self.delimiter = delimiter
        self.block_delimiter = block_delimiter or {}

    def _split_block(self, name, header, explicit):
        # The block type pattern also matches '-' and '_', so a delimiter written
        # right after it (e.g. "/// caption- text") may have been captured as part
        # of the name: give trailing characters back until the delimiter is found
        for end in range(len(name), 0, -1):
            block, rest = name[:end], name[end:] + header
            delimiter = explicit or self.block_delimiter.get(block, self.delimiter)
            found = rest.startswith(delimiter) if end < len(name) else delimiter in rest
            if found:
                return block, delimiter, rest.strip()
        return None

    def run(self, lines):
        new_lines = []
        for line in lines:
            m = self.HEADER_RE.match(line)
            if m:
                indent = m.group("indent") or ""
                slashes = m.group("slashes")
                split = self._split_block(m.group("block"), m.group("header"), m.group("delimiter"))

                if split is None or split[0] in self.exclude_blocks:
                    new_lines.append(line)
                    continue

                block, delimiter, header = split
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
            "block_delimiter": [{}, "Dictionary for specifying a default delimiter for specific block types"],
        }
        super().__init__(**kwargs)
        self._validate_delimiters()

    def _validate_delimiters(self):
        block_delimiter = self.getConfig("block_delimiter")
        if not isinstance(block_delimiter, dict):
            raise ValueError(
                f"inline_blocks: 'block_delimiter' must be a dictionary, got {block_delimiter!r}"
            )

        delimiters = {"delimiter": self.getConfig("delimiter")}
        delimiters.update({f"block_delimiter[{block!r}]": d for block, d in block_delimiter.items()})
        for name, delimiter in delimiters.items():
            if not isinstance(delimiter, str) or not delimiter:
                raise ValueError(
                    f"inline_blocks: '{name}' must be a non-empty string, got {delimiter!r}"
                )

    def extendMarkdown(self, md):
        # Run after SuperFences ("fenced_code_block", priority 25), so fenced
        # code is already stashed and its content is left untouched
        md.preprocessors.register(
            InlineBlockPreprocessor(
                md,
                exclude_blocks=self.getConfig("exclude_blocks"),
                delimiter=self.getConfig("delimiter"),
                block_delimiter=self.getConfig("block_delimiter"),
            ),
            "inline_blocks",
            24,
        )


def makeExtension(**kwargs):
    return InlineBlockExtension(**kwargs)

