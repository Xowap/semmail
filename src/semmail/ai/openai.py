import os

import lazy_object_proxy
from openai import OpenAI, OpenAIError

from semmail.utils.func import retry

client = lazy_object_proxy.Proxy(lambda: OpenAI(api_key=os.environ["OPENAI_API_KEY"]))


@retry(OpenAIError)
def ask_closed_ai(prompt: str, text: str):
    """
    Asks OpenAI a given prompt with a given text as a parameter. This is a very
    think wrapper around OpenAI's API and also provides a retry mechanism in
    order to counter potential failures.

    Parameters
    ----------
    prompt
        Prompt to ask
    text
        Your function's input
    """

    chat_messages = [
        dict(role="system", content=prompt),
        dict(role="user", content=text),
    ]

    response = client.chat.completions.create(model="gpt-4", messages=chat_messages)

    return response.choices[0].message.content
