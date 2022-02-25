from typing import List

import spacy
from selectolax.parser import HTMLParser
from spacy.tokenizer import Tokenizer


class HTMLTokenizer(Tokenizer):
    def __init__(
        self,
        unwrap_tags: List[str] = ["em", "strong", "b", "i", "span", "a", "code", "kbd"],
        remove_tags: List[str] = ["script", "style"],
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.unwrap_tags = unwrap_tags
        self.remove_tags = remove_tags

    def __call__(self, string) -> spacy.tokens.Doc:

        html_texts = self.parse_html(string)
        html_docs = []
        for text in html_texts:
            html_doc = super().__call__(text)
            html_docs.append(html_doc)
        doc = spacy.tokens.Doc.from_docs(html_docs)
        return doc

    def parse_html(self, html_string: str) -> List[str]:
        parsed_html = HTMLParser(html_string)
        for removed_tag in self.remove_tags:
            for element in parsed_html.css(removed_tag):
                element.decompose()

        parsed_html.unwrap_tags(self.unwrap_tags)
        html_texts = []
        for node in parsed_html.css("*"):
            # selectolax `strip=True` will merge unwrapped tag texts together
            # so we need regular python strip()
            node_text = node.text(deep=False, strip=False)
            node_text = node_text.strip()
            node_text = node_text.replace("\n", " ")
            if node_text:
                html_texts.append(node_text)
        return html_texts


@spacy.registry.tokenizers("html_tokenizer")
def create_html_tokenizer(
    unwrap_tags: List[str] = ["em", "strong", "b", "i", "span", "a", "code", "kbd"],
    remove_tags: List[str] = ["script", "style"],
):
    def create_tokenizer(nlp) -> Tokenizer:
        tokenizer = HTMLTokenizer(
            vocab=nlp.vocab,
            rules=nlp.tokenizer.rules,
            prefix_search=nlp.tokenizer.prefix_search,
            suffix_search=nlp.tokenizer.suffix_search,
            infix_finditer=nlp.tokenizer.infix_finditer,
            token_match=nlp.tokenizer.token_match,
            url_match=nlp.tokenizer.url_match,
            unwrap_tags=unwrap_tags,
            remove_tags=remove_tags,
        )
        return tokenizer

    return create_tokenizer
