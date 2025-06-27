# Literally

 Literally is a tool for semi-literate programming.

 Unlike real literate programming tools, Literally does not rearrange your code.

 This is very much a rewrite of [pycco](https://github.com/pycco-docs/pycco), which itself
 is a Python port of [Docco](https://github.com/jashkenas/docco).


## The code

```python

import re
import argparse
import pygments
from typing import TypedDict, List, Tuple
from dataclasses import dataclass
```

I use snoop for print debugging.
import snoop

### Utility functions

```python
def running(f, iterable, init=None):
```


Calculate a running value from an iterable using a binary function `f`.



```python
    for x in iterable:
        init = x if init is None else f(init, x)
        yield init


def running_sum(iterable, init=None):
```


Calculate a running sum.
``` python
>> list(running_sum(range(5)))
[0, 1, 3, 6, 10, 15]
>> list(running_sum(range(5), 10))
[10, 11, 13, 16, 20, 25]
```



```python
    return running(lambda x, y: x + y, iterable, init)


def indent_size(s: str) -> int:
```

A string's indent size is the number of leading spaces.

```python
    for i, c in enumerate(s):
        if c != " ":
            return i
    return len(s)


def dedent(s: List[str]) -> List[str]:
    min_indent = min(indent_size(line) for line in s)
    return [line[min_indent:] for line in s]
```

### Extracting chunks

```python
def parse_blockquote(
    contents: List[str], block_syms: Tuple[str, str]
) -> Tuple[List[int], List[int]]:
```


Parse out blockquotes from a list of contents.



```python
    is_blockquote = [
        1 if c.startswith(block_syms[0]) else -1 if c.startswith(block_syms[1]) else 0
        for c in contents
    ]
    if block_syms[0] == block_syms[1]:
```

if the block start and end are the same string, we need to treat
every other blockquote as an end.

```python
        is_start = 1
        for i, b in enumerate(is_blockquote):
            if b == 1:
                is_blockquote[i] = is_start
                is_start = -is_start
    level = list(running_sum(is_blockquote))
    assert level[-1] == 0, "Unmatched blockquote start/end"
    return is_blockquote, level


def extract_chunks(
    code: str, comment_start: str, block_syms: Tuple[str, str]
) -> Tuple[List[str], List[str]]:
```


Extract doc and code chunks from a program. We return a list of chunks
and a list of booleans indicating whether each chunk is a doc chunk.



```python
    lines = code.splitlines(keepends=True)
    lc = len(lines)  # line count
```

Contents are lines stripped of leading whitespace. We strip leading
whitespaces only to minimize changes.

```python
    contents = [line.lstrip() for line in lines]
    is_comment = [c.startswith(comment_start) for c in contents]
    is_blockquote, level = parse_blockquote(contents, block_syms)
```

Chunks are consecutive lines. Docs are chunks that are comments or blockquoted.

```python
    is_doc = [is_comment[i] or is_blockquote[i] or level[i] != 0 for i in range(lc)]
```

Chunks are always interspersed, meaning that for each two doc chunks
there is a code chunk in between, and vice versa.

```python
    is_chunk_top = [i == 0 or is_doc[i - 1] != is_doc[i] for i in range(lc)]
    chunk_top_loc = [i for i, v in enumerate(is_chunk_top) if v]
    chunk_bottom_loc = chunk_top_loc[1:] + [lc]
```

doc chunks are stripped of its starting symbols and whitespaces,
while code chunks are left as is.

```python
    def strip(i: int, s: str) -> str:
        if is_comment[i]:
            return contents[i].removeprefix(comment_start)
        if is_blockquote[i] != 0:
            return contents[i].removeprefix(block_syms[0]).removesuffix(block_syms[1])
        if is_doc[i]:
            return contents[i]
        return s

    chunk_lines = [strip(i, s) for i, s in enumerate(lines)]
    chunk_type = ["doc" if is_doc[i] else "code" for i in chunk_top_loc]
    chunks = [
        "".join(chunk_lines[i:j]) for i, j in zip(chunk_top_loc, chunk_bottom_loc)
    ]
    return chunk_type, chunks
```

### Formatting

```python
def highlight(code_chunks: List[str], language: str, comment_start: str) -> List[str]:
```


Highlight all code chunks in one pass to pygments,
which is more efficient than highlighting each chunk separately.



Magic divider text and html copied from pycco.

```python
    divider_text = f"\n{comment_start}DIVIDER\n"
    divider_html = re.compile(
        rf'\n*<span class="c[1]?">{comment_start}DIVIDER</span>\n*'
    )
    lexer = pygments.lexers.get_lexer_by_name(language)
```

To do this, we join all code chunks into a single program
with a piece of divider text in between,

```python
    joined_code = divider_text.join(code_chunks)
```

highlight the whole thing using pygments,

```python
    html_formatter = pygments.formatters.get_formatter_by_name("html")
    output = (
        pygments.highlight(joined_code, lexer, html_formatter)
        .replace('<div class="highlight"><pre>', "")
        .replace("</pre></div>", "")
    )
```

then split it into html to get the html for each code section.

```python
    return re.split(divider_html, output)
```

### Command line interface

```python
def main():
    with open("literally.py", "r") as f:
        code = f.read()
    chunk_type, chunks = extract_chunks(code, "#", ('"""', '"""'))
    readme_md = []
    for i, s in enumerate(chunks):
        if chunk_type[i] == "doc":
            readme_md.append("".join(dedent(s.splitlines(keepends=True))))
        else:
```

we strip trailing whitespace to make the output slightly cleaner.

```python
            s = s.rstrip()
            if s != "":
                readme_md.append(f"```python\n{s}\n```\n")
    with open("README.md", "w") as f:
        f.write("\n".join(readme_md))


if __name__ == "__main__":
    main()
```
