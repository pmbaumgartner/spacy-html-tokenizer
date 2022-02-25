# HTML-friendly spaCy Tokenizer

It's not an [HTML tokenizer](https://www.w3.org/TR/2011/WD-html5-20110113/tokenization.html#tokenization), but a tokenizer that works with text that happens to be embedded in HTML. 

## How it works

Under the hood we use [`selectolax`](https://github.com/rushter/selectolax) to parse HTML. From there, common elements used for styling within traditional text elements elements (e.g. `<b>` or `<span>` inside of a `<p>`) are [unwrapped](https://selectolax.readthedocs.io/en/latest/parser.html#selectolax.parser.HTMLParser.unwrap_tags), meaning the text contained within those elements becomes nested inside their parent elements. You can change this with the `unwrapped_tags` argument to the constructor. Tags used for non-text content, such as `<script>` and `<style>` are removed. Then the text is extracted from each remaining terminal node that contains text. These texts are then tokenized with the standard tokenizer defaults and then combined into a single `Doc`. The end result is a `Doc`, but each element's text from the original document is also a [sentence](https://spacy.io/api/doc#sents), so you can iterate through each element's text with `doc.sents`.

## Example

```python
import spacy
from spacy_html_tokenizer import create_html_tokenizer

nlp = spacy.blank("en")
nlp.tokenizer = create_html_tokenizer()(nlp)

html = """<h2>An Ordered HTML List</h2>
<ol>
    <li><b>Good</b> coffee. There's another sentence here</li>
    <li>Tea and honey</li>
    <li>Milk</li>
</ol>"""

doc = nlp(html)
for sent in doc.sents:
    print(sent.text, "-- N Tokens:", len(sent))

# An Ordered HTML List -- N Tokens: 4
# Good coffee. There's another sentence here -- N Tokens: 8
# Tea and honey -- N Tokens: 3
# Milk -- N Tokens: 1
```

In the prior example, we didn't have any other sentence boundary detection components. However, this will also work with downstream sentence boundary detection components -- e.g.

```python
nlp = spacy.load("en_core_web_sm")  # has parser for sentence boundary detection
nlp.tokenizer = create_html_tokenizer()(nlp)

doc = nlp(html)
for sent in doc.sents:
    print(sent.text, "-- N Tokens:", len(sent))

# An Ordered HTML List -- N Tokens: 4
# Good coffee. -- N Tokens: 3
# There's another sentence here -- N Tokens: 5
# Tea and honey -- N Tokens: 3
# Milk -- N Tokens: 1
```

### Comparison

We'll compare parsing [Explosion's About page](https://explosion.ai/about) with and without the HTML tokenizer.

```python
import requests
import spacy
from spacy_html_tokenizer import create_html_tokenizer
from selectolax.parser import HTMLParser

about_page_html = requests.get("https://explosion.ai/about").text

nlp_default = spacy.load("en_core_web_lg")
nlp_html = spacy.load("en_core_web_lg")
nlp_html.tokenizer = create_html_tokenizer()(nlp_html)

# text from HTML - used for non-HTML default tokenizer
about_page_text = HTMLParser(about_page_html).text()

doc_default = nlp_default(about_page_text)
doc_html = nlp_html(about_page_html)
```

#### View first sentences of each

With standard tokenizer on text extracted from HTML

```python
list(sent.text for sent in doc_default.sents)[:5]
```

```python
['AboutSoftware & DemosCustom SolutionsBlog & NewsAbout usExplosion is a software company specializing in developer tools for Artificial\nIntelligence and Natural Language Processing.',
'We’re the makers of\nspaCy, one of the leading open-source libraries for advanced\nNLP and Prodigy, an annotation tool for radically efficient\nmachine teaching.',
'\n\n',
'Ines Montani CEO, FounderInes is a co-founder of Explosion and a core developer of the spaCy NLP library and the Prodigy annotation tool.',
'She has helped set a new standard for user experience in developer tools for AI engineers and researchers.']
```

With HTML Tokenizer on HTML

```python
list(sent.text for sent in doc_html.sents)[:10]
```

```python
['About us · Explosion',
 'About',
 'Software',
 '&',
 'Demos',
 'Custom Solutions',
 'Blog & News',
 'About us',
 'Explosion is a software company specializing in developer tools for Artificial Intelligence and Natural Language Processing.',
 'We’re the makers of spaCy, one of the leading open-source libraries for advanced NLP and Prodigy, an annotation tool for radically efficient machine teaching.']
```

What about the last sentence?

```python
list(sent.text for sent in doc_default.sents)[-1]

# We’re the makers of spaCy, one of the leading open-source libraries for advanced NLP.NavigationHomeAbout usSoftware & DemosCustom SolutionsBlog & NewsOur SoftwarespaCy · Industrial-strength NLPProdigy · Radically efficient annotationThinc · Functional deep learning© 2016-2022 Explosion · Legal & Imprint/*<![CDATA[*/window.pagePath="/about";/*]]>*//*<![CDATA[*/window.___chunkMapping={"app":["/app-ac229f07fa81f29e0f2d.js"],"component---node-modules-gatsby-plugin-offline-app-shell-js":["/component---node-modules-gatsby-plugin-offline-app-shell-js-461e7bc49c6ae8260783.js"],"component---src-components-post-js":["/component---src-components-post-js-cf4a6bf898db64083052.js"],"component---src-pages-404-js":["/component---src-pages-404-js-b7a6fa1d9d8ca6c40071.js"],"component---src-pages-blog-js":["/component---src-pages-blog-js-1e313ce0b28a893d3966.js"],"component---src-pages-index-js":["/component---src-pages-index-js-175434c68a53f68a253a.js"],"component---src-pages-spacy-tailored-pipelines-js":["/component---src-pages-spacy-tailored-pipelines-js-028d0c6c19584ef0935f.js"]};/*]]>*/
```

Yikes. How about HTML Tokenizer?

```python
list(sent.text for sent in doc_html.sents)[-1]

# '© 2016-2022 Explosion · Legal & Imprint'
```
