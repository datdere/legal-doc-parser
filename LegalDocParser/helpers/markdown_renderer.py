import markdown
from markdown.extensions.tables import TableExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.toc import TocExtension


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<style>
body {{
    font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
    line-height: 1.8;
    max-width: 900px;
    margin: 0 auto;
    padding: 20px;
    color: #333;
    background: #fff;
}}
h1, h2, h3, h4, h5, h6 {{
    color: #1a1a2e;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
}}
table {{
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
}}
th, td {{
    border: 1px solid #ddd;
    padding: 8px 12px;
    text-align: left;
}}
th {{
    background-color: #f5f5f5;
    font-weight: bold;
}}
tr:nth-child(even) {{
    background-color: #fafafa;
}}
pre {{
    background-color: #f4f4f4;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 12px;
    overflow-x: auto;
}}
code {{
    background-color: #f4f4f4;
    padding: 2px 5px;
    border-radius: 3px;
    font-size: 0.9em;
}}
blockquote {{
    border-left: 4px solid #1a1a2e;
    margin: 1em 0;
    padding: 0.5em 1em;
    background: #f9f9f9;
}}
</style>
</head>
<body>
{content}
</body>
</html>"""


def render_markdown_to_html(md_text: str) -> str:
    extensions = [
        TableExtension(),
        FencedCodeExtension(),
        CodeHiliteExtension(guess_lang=False),
        TocExtension(),
        "nl2br",
    ]
    html_body = markdown.markdown(md_text, extensions=extensions)
    return HTML_TEMPLATE.format(content=html_body)


def render_plain_text_to_html(text: str) -> str:
    import html as html_module
    escaped = html_module.escape(text)
    content = f"<pre><code>{escaped}</code></pre>"
    return HTML_TEMPLATE.format(content=content)
