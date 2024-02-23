from dataclasses import dataclass
from textwrap import dedent
from typing import Any


@dataclass
class Prompt:
    prompt: str
    schema: Any


DETERMINE_TYPE = Prompt(
    prompt=dedent(
        """
        Take a deep breath.

        You will analyze an email. For this email you need to determine the
        likeliness that this email belongs to a specific category. This works
        with a score system. For each category you MUST give a score of 0 if
        you are sure that it's not from that category, a score of 1 if you are
        sure or a number between 0 or 1 that reflects how much you want to
        give that category to the email.

        The categories are:
            - Commercial is a prospective email.
            - Bill is an invoice or a bill for a sold service or product.
            - Conversation is a regular conversation between humans.

        Here are elements to look for in an email. For each element, if I tell 
        you +X then consider that it's adding points to that aspect and -X is 
        removing points.

        Has few sentences +bill -commercial
        Has a total price +bill
        Has a list of items sold +bill
        Has "bill", "invoice", "order confirmation" or any synonym in the Subject +bill -commercial -conversation
        Presents several product benefits +commercial -bill
        Is structured in a Hello/Message/Signature way +conversation -bill
        Different signatures and quoted mails +conversation -bill -commercial

        Now return the following YAML:

        bill: x
        commercial: x
        conversation: x

        You need to replace "x" by the score. If you want to give a score of
        1 to two or more categories, you need to think harder to make the
        difference.

        Make sure that the output is pure YAML, not wrapped in Markdown, no sentences.
        """
    ),
    schema={
        "type": "object",
        "properties": {
            "commercial": {"type": "number", "minimum": 0, "maximum": 1},
            "bill": {"type": "number", "minimum": 0, "maximum": 1},
            "conversation": {"type": "number", "minimum": 0, "maximum": 1},
        },
        "required": ["commercial", "bill", "conversation"],
    },
)

COMMERCIAL_INFO = Prompt(
    prompt=dedent(
        """
        This email seems to be a commercial email. We want to determine what is
        the proposed product and what is its offered value.

        Please output exclusively a parseable YAML with the following structure:

        product: "x"
        usp: "x"

        With product being the name of the product and usp the unique selling
        proposition.
        """
    ),
    schema={
        "type": "object",
        "properties": {
            "product": {"type": "string"},
            "usp": {"type": "string"},
        },
        "required": ["product", "usp"],
    },
)

BILL_INFO = Prompt(
    prompt=dedent(
        """
        This emails contains a bill or an invoice. We want to know all the
        products or services that were bought if possible, as well as the total
        amount paid.

        All amounts must follow the [42, "EUR"]/[12, "USD"]/etc formalism, 
        where the first item of the list is the float amount and the second is
        the ISO code of the currency.

        Here is an example output:

        total: [x, x]  # Total amount of the invoice

        Now if you see a list of items or services bought, you can add the
        following key to the output:

        bought: []  # List of items bought

        And for each item you find, add it to the bought list. One item has the
        following structure:

        label: "x"
        price: [x, x]

        The label corresponds to the label you found and the price is the price
        of that specific item, in the format defined above.

        You must output exclusively a parseable YAML following the example
        from above.
        """
    ),
    schema={
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "bought": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "label": {"type": "string"},
                        "price": {
                            "type": "array",
                            "items": [{"type": "number"}, {"type": "string"}],
                            "minItems": 2,
                            "maxItems": 2,
                        },
                    },
                    "required": ["label", "price"],
                },
            },
            "total": {
                "type": "array",
                "items": [{"type": "number"}, {"type": "string"}],
                "minItems": 2,
                "maxItems": 2,
            },
        },
        "required": ["total"],
    },
)

CONVERSATION_INFO = Prompt(
    prompt=dedent(
        """
        The following email contains a conversation. Please summarize the
        latest message in the following YAML structure:

        summary: "x"

        x is a summary of the message

        Be careful to output valid YAML and only YAML, no sentence around.
        """
    ),
    schema=dict(
        type="object",
        required=["summary"],
        properties={
            "summary": {"type": "string"},
        },
    ),
)
