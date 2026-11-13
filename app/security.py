import html


def escape_html(value):
    """Escape untrusted text before inserting it into an HTML response."""
    return html.escape(str(value), quote=True)
