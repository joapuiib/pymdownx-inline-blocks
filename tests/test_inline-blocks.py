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
