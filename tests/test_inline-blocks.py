import re

import markdown
import pytest
from inline_blocks import InlineBlockExtension

MD = markdown.Markdown(extensions=['inline_blocks'])

def render(text: str, md=None) -> str:
    if md is None:
        md = MD

    # Preprocessors run before conversion to HTML.
    return "\n".join(md.preprocessors['inline_blocks'].run(text.splitlines()))


def test_simple_attribution():
    input_text = "/// attribution: Unknown author"
    expected = "\n".join([
        "/// attribution",
        "Unknown author",
        "///"
    ])
    assert render(input_text) == expected


def test_block_with_modifiers():
    input_text = "/// figure-caption | < ^1 : Caption"
    expected = "\n".join([
        "/// figure-caption | < ^1",
        "Caption",
        "///"
    ])
    assert render(input_text) == expected


def test_multiple_blocks_in_sequence():
    input_text = "\n".join([
        "![img](placeholder.png)",
        "/// attribution: Unknown author",
        "/// figure-caption | < ^1 : Caption",
    ])
    expected = "\n".join([
        "![img](placeholder.png)",
        "/// attribution",
        "Unknown author",
        "///",
        "/// figure-caption | < ^1",
        "Caption",
        "///"
    ])
    assert render(input_text) == expected


def test_non_matching_lines_pass_through():
    input_text = "This is a normal line."
    expected = "This is a normal line."
    assert render(input_text) == expected


def test_trims_extra_spaces():
    input_text = "/// attribution:   Some author   "
    expected = "\n".join([
        "/// attribution",
        "Some author",
        "///"
    ])
    assert render(input_text) == expected


@pytest.mark.parametrize("line", [
    "///not-valid",   # missing space after ///
    "/// block only", # no colon
    "/// : no block", # no block type
])
def test_invalid_lines_remain_unchanged(line):
    assert render(line) == line


def test_more_slashes():
    input_text = "///// attribution: Extra slashes"
    expected = "\n".join([
        "///// attribution",
        "Extra slashes",
        "/////"
    ])
    assert render(input_text) == expected


def test_leading_indentation():
    input_text = "    /// attribution: Indented author"
    expected = "\n".join([
        "    /// attribution",
        "    Indented author",
        "    ///"
    ])
    assert render(input_text) == expected


def test_exclude_html_by_default():
    input_text = '/// html | div[style="display flex; gap: 1em; flex-direction: column;]'
    assert render(input_text) == input_text


def test_include_html_if_no_exclusions():
    md = markdown.Markdown(extensions=[InlineBlockExtension(exclude_blocks=[])])
    input_text = '/// html | p : Content'
    expected = "\n".join([
        "/// html | p",
        "Content",
        "///"
    ])
    assert render(input_text, md) == expected


def test_exclude():
    md = markdown.Markdown(extensions=[InlineBlockExtension(exclude_blocks=["attribution"])])
    input_text = '/// attribution: Some author'
    assert render(input_text, md) == input_text


def test_delimiter():
    input_text = "///! caption | [style=\"color: red;\"] ! A red caption."
    expected = "\n".join([
        "/// caption | [style=\"color: red;\"]",
        "A red caption.",
        "///"
    ])
    assert render(input_text) == expected


def test_config_delimiter():
    md = markdown.Markdown(extensions=[InlineBlockExtension(delimiter="!")])
    input_text = "/// caption | [style=\"color: red;\"] ! A red caption."
    expected = "\n".join([
        "/// caption | [style=\"color: red;\"]",
        "A red caption.",
        "///"
    ])
    assert render(input_text, md) == expected


def test_config_block_delimiter():
    md = markdown.Markdown(extensions=[InlineBlockExtension(block_delimiter={"caption": "!"})])
    input_text = "/// caption | [style=\"color: red;\"] ! A red caption."
    expected = "\n".join([
        "/// caption | [style=\"color: red;\"]",
        "A red caption.",
        "///"
    ])
    assert render(input_text, md) == expected


def test_config_block_delimiter_override():
    md = markdown.Markdown(extensions=[InlineBlockExtension(block_delimiter={"caption": "!"})])
    input_text = "///+ caption | [style=\"color: red;\"] + A red caption."
    expected = "\n".join([
        "/// caption | [style=\"color: red;\"]",
        "A red caption.",
        "///"
    ])
    assert render(input_text, md) == expected


@pytest.mark.parametrize("line, kwargs", [
    ("/// caption- A caption.", {"delimiter": "-"}),
    ("///- caption- A caption.", {}),
    ("/// caption_ A caption.", {"block_delimiter": {"caption": "_"}}),
])
def test_delimiter_after_block_name(line, kwargs):
    md = markdown.Markdown(extensions=[InlineBlockExtension(**kwargs)])
    expected = "\n".join([
        "/// caption",
        "A caption.",
        "///"
    ])
    assert render(line, md) == expected


def test_hyphenated_block_with_hyphen_delimiter():
    md = markdown.Markdown(extensions=[InlineBlockExtension(delimiter="-")])
    input_text = "/// figure-caption - A caption."
    expected = "\n".join([
        "/// figure-caption",
        "A caption.",
        "///"
    ])
    assert render(input_text, md) == expected


@pytest.mark.parametrize("line", [
    "///caption: A caption.",
    "///   caption: A caption.",
])
def test_block_without_space_after_slashes(line):
    expected = "\n".join([
        "/// caption",
        "A caption.",
        "///"
    ])
    assert render(line) == expected


def test_inline_delimiter_requires_whitespace():
    input_text = "///+caption: A caption."
    assert render(input_text) == input_text


@pytest.mark.parametrize("kwargs, message", [
    ({"delimiter": ""}, "'delimiter' must be a non-empty string"),
    ({"delimiter": None}, "'delimiter' must be a non-empty string"),
    ({"block_delimiter": {"caption": ""}}, "'block_delimiter['caption']' must be a non-empty string"),
    ({"block_delimiter": {"caption": 1}}, "'block_delimiter['caption']' must be a non-empty string"),
    ({"block_delimiter": ["caption"]}, "'block_delimiter' must be a dictionary"),
])
def test_invalid_delimiter_config(kwargs, message):
    with pytest.raises(ValueError, match=re.escape(message)):
        InlineBlockExtension(**kwargs)


def convert(text: str) -> str:
    # inline_blocks is listed first, so it only runs after SuperFences thanks to its priority
    md = markdown.Markdown(extensions=[
        'inline_blocks', 'pymdownx.superfences', 'pymdownx.blocks.caption', 'admonition',
    ])
    return md.convert(text)


@pytest.mark.parametrize("fence", ["```", "~~~", "````"])
def test_fenced_code_is_not_processed(fence):
    input_text = "\n".join([
        f"{fence}markdown",
        "/// caption: Inside",
        fence,
    ])
    assert "/// caption: Inside" in convert(input_text)


def test_indented_fenced_code_is_not_processed():
    input_text = "\n".join([
        '!!! example "Markdown"',
        "",
        "    ```markdown",
        "    /// caption | .spell-ignore : Inside",
        "    ```",
    ])
    assert "/// caption | .spell-ignore : Inside" in convert(input_text)


def test_blocks_after_fenced_code_are_processed():
    input_text = "\n".join([
        "```markdown",
        "/// caption: Inside",
        "```",
        "",
        "/// caption: Outside",
    ])
    html = convert(input_text)
    assert "/// caption: Inside" in html
    assert "<p>Outside</p>" in html
