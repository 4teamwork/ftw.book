import re


def cleanup_standalone_html_tags(html):
    """Standalone HTML tags should be ended with a slash ("/>" instead of ">")
    """

    standalone_tags = ('br',
                       )

    for tag in standalone_tags:
        xpr = re.compile(r'<(%s[^>/]*?)>' % tag)
        html = xpr.sub(r'<\1/>', html)

    return html
