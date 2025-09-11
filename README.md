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
