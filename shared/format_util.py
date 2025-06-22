def format_user_messages_with_index(messages):
    return "\n".join(f"{idx + 1}. {msg}" for idx, msg in enumerate(messages))


def to_html_format(html_body):
    html_content = f"""<!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>여행 계획 공유</title>
    </head>
    <body>
    {html_body}
    </body>
    </html>
    """
    return html_content
