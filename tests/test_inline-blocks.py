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
