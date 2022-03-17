from pathlib import Path

import pytest
import spacy
import tomli
from src.spacy_html_tokenizer import __version__, create_html_tokenizer


def test_version():
    version = "0.1.2"
    pyproject = tomli.loads(Path("pyproject.toml").read_text())
    assert pyproject["tool"]["poetry"]["version"] == version
    assert __version__ == version


@pytest.fixture
def tokenizer():
    nlp = spacy.blank("en")
    tokenizer = create_html_tokenizer()(nlp)
    return tokenizer


@pytest.fixture
def pipeline():
    nlp = spacy.load("en_core_web_sm", disable=["tagger", "ner", "lemmatizer"])
    nlp.tokenizer = create_html_tokenizer()(nlp)
    return nlp


@pytest.fixture
def html1():
    html = """<h2>An Ordered HTML List</h2>
    <ol>
        <li><b>Good</b> Coffee. There's another sentence here</li>
        <li>Tea and honey</li>
        <li>Milk</li>
    </ol>"""
    return html


@pytest.fixture
def html2():
    html = """
    <body>
        <span id="vspan"></span>
        <h1>Welcome to selectolax tutorial</h1>
        <div id="text">
            <p class='p3' style='display:none;'>Excepteur <i>sint</i> occaecat cupidatat non proident</p>
            <p class='p3' vid>Lorem ipsum</p>
        </div>
        <div>
            <p id='stext'>Lorem ipsum dolor sit amet, ea quo modus meliore platonem.</p>
        </div>
    </body>
    """
    return html


@pytest.fixture
def html_with_script():
    html = """<h2>An Ordered HTML List</h2>
    <script>pretend some javascript is here</script>"""
    return html


def test_html1(tokenizer, html1):
    sent_starts = [0, 4, 12, 15]
    doc = tokenizer(html1)

    assert len(doc) == 16
    assert len(list(doc.sents)) == 4
    for i, token in enumerate(doc):
        if i in sent_starts:
            assert token.is_sent_start
        if i not in sent_starts:
            assert token.is_sent_start is None


def test_html2(tokenizer, html2):
    sent_starts = [0, 4, 10, 12]
    doc = tokenizer(html2)

    assert len(doc) == 24
    assert len(list(doc.sents)) == 4
    for i, token in enumerate(doc):
        if i in sent_starts:
            assert token.is_sent_start
        if i not in sent_starts:
            assert token.is_sent_start is None


def test_html1_with_sentence_boundary(pipeline, html1):
    doc = pipeline(html1)
    # We include the dependency parser in this one to check that
    # additional sentence boundary detection still works
    assert len(list(doc.sents)) == 5


def test_html_with_script(pipeline, html_with_script):
    doc = pipeline(html_with_script)
    assert len(list(doc.sents)) == 1
