from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
from quopri import decodestring
from typing import Any

import html2text

from .ai import parse_to_json
from .prompts import BILL_INFO, COMMERCIAL_INFO, CONVERSATION_INFO, DETERMINE_TYPE


def html_to_text(html_content):
    """
    Converts HTML into more or less readable text. This will clarify the
    message for the AI later on (also, it will use a lot less tokens).

    Parameters
    ----------
    html_content
        Content of the email
    """

    h = html2text.HTML2Text()
    h.ignore_links = True
    return h.handle(html_content)


def decode_content(part):
    """Honestly I don't even know what this does, ChatGPT wrote it. The
    encoding of emails is such a fucking mess."""

    content_transfer_encoding = part.get("Content-Transfer-Encoding", "").lower()
    payload = part.get_payload(decode=True)  # Decode base64 or quoted-printable
    if content_transfer_encoding == "quoted-printable":
        # Ensure correct handling of quoted-printable encoding
        payload = decodestring(payload)
    try:
        # Assume the charset is properly defined, fallback to UTF-8 if not
        charset = part.get_content_charset() or "utf-8"
        return payload.decode(charset)
    except (LookupError, UnicodeDecodeError):
        # Fallback in case of unknown or incorrect charset
        return payload.decode("utf-8", errors="replace")


def find_all_parts(message: EmailMessage):
    """Recursively dig into all multipart messages in order to find the parts
    that are just regular messages"""

    stack = [message]

    while stack:
        msg = stack.pop()

        if msg.is_multipart():
            for part in msg.iter_parts():
                stack.append(part)
        else:
            yield msg


def decode_part(message: EmailMessage) -> str:
    """Decodes an email by -- ideally -- parsing the HTML into Markdown and
    returning that, or falling back to the text content. The conversion to
    Markdown is of course to save up on tokens and context size."""

    text_content = ""
    html_content = ""

    for part in find_all_parts(message):
        if part.get_content_type() == "text/plain":
            text_content = decode_content(part)
        elif part.get_content_type() == "text/html":
            html_content = html_to_text(decode_content(part))

    return html_content or text_content


def parse_email(message_raw: bytes):
    """
    In order to make AI work on the email, we need to sort out what we want to
    keep and remove the junk.

    In terms of headers, we'll just keep the basic ones so that the LLM can
    have a bit of context.

    In terms of email, we'll prioritize getting the HTML content of the email
    because it is usually better tested by websites than the pure text one
    (sad but true). However if the HTML content can't be found or parsed we'll
    fall back to the plain text one.

    Parameters
    ----------
    message_raw
        The bytes from this email
    """

    # noinspection PyTypeChecker
    message: EmailMessage = BytesParser(policy=policy.default).parsebytes(message_raw)

    from_ = message.get("From", "")
    to = message.get("To", "")
    date = message.get("Date", "")
    subject = message.get("Subject", "")
    payload = decode_part(message)

    return f"From: {from_}\nTo: {to}\nDate: {date}\nSubject: {subject}\n\n{payload}"


def interpret_email(email: bytes) -> Any:
    """Uses a first round of LLM in order to determine the type of message,
    then proceeds to using a specific prompt for that type in order to parse
    the email into a JSON output."""

    parsed_email = parse_email(email)

    email_type_proba = parse_to_json(
        DETERMINE_TYPE.prompt,
        parsed_email,
        DETERMINE_TYPE.schema,
    )

    email_type = max(email_type_proba.items(), key=lambda p: p[1])[0]
    extra = {}

    if email_type == "commercial":
        extra["commercial"] = parse_to_json(
            COMMERCIAL_INFO.prompt,
            parsed_email,
            COMMERCIAL_INFO.schema,
        )
    elif email_type == "bill":
        extra["bill"] = parse_to_json(
            BILL_INFO.prompt,
            parsed_email,
            BILL_INFO.schema,
        )
    elif email_type == "conversation":
        extra["conversation"] = parse_to_json(
            CONVERSATION_INFO.prompt,
            parsed_email,
            CONVERSATION_INFO.schema,
        )

    return dict(
        email_type=dict(
            chosen=email_type,
            proba=email_type_proba,
        ),
        **extra,
    )
