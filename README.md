# PyMdown Inline Blocks
A Python Markdown extension to convert inline block shorthand syntax into [PyMdown Block Extension][pymdownx-block] format

[pymdownx-block]: https://facelessuser.github.io/pymdown-extensions/extensions/blocks/

- Convert single-line inline block syntax into fully-formed block syntax.
- Supports modifiers for advanced block formatting.
- Simple and lightweight; integrates easily with Markdown or MkDocs.


## Example
The following markdown inline block syntax:

```markdown
![img](placeholder.png)
/// attribution: Unknown author
/// figure-caption | < ^1 : Caption
```

Will be converted to the following PyMdown Block syntax:

```markdown
![img](placeholder.png)
/// attribution
Unknown author
///
/// figure-caption | < ^1
Caption
///
```


## Installation
Install the extension via pip:

```bash
pip install pymdownx-inline-blocks
```


## Usage
To use the extension, add it to your Markdown or MkDocs configuration:

```python
md = markdown.Markdown(extensions=['inline_blocks'])
```

or, if using MkDocs, add it to your `mkdocs.yml`:

```yaml
markdown_extensions:
  - inline_blocks
```

## Options
The extension supports the following options:

- `exclude_blocks`: A list of block types to exclude from processing. Default is `['html']`.
- `delimiter`: The delimiter used to separate the block and the content. Default is `:`.
- `block_delimiter`: A dictionary mapping block types to their own default delimiter, overriding `delimiter` for those blocks. Default is `{}`.

For example, to use `!` as the delimiter for `caption` blocks only:

```yaml
markdown_extensions:
  - inline_blocks:
      block_delimiter:
        caption: "!"
```

Delimiters must be non-empty strings; otherwise the extension raises a `ValueError` when it is loaded.

The delimiter can also be set for a single line by writing it right after the slashes, followed by a space. It takes precedence over both options:

```markdown
///! caption | [style="color: red;"] ! A red caption.
```
