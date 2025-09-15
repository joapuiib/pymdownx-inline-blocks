import markdown
import pytest
from inline_blocks import InlineBlockExtension

md = markdown.Markdown(extensions=['inline_blocks'])


def render(text: str) -> str:
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
