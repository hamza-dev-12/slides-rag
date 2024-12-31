import re

def format_bold_text(text):
    """
    Convert markdown-style **bold text** into HTML <strong> tags.
    
    Arguments:
    text (str): Input string with markdown-style bold syntax.

    Returns:
    str: String with <strong> tags for bold text.
    """
    return re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)