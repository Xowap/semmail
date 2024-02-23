from os import environ
from typing import Dict, Sequence

import lazy_object_proxy
import torch
from huggingface_hub import login
from lark import Lark, Transformer
from transformers import AutoModelForCausalLM, AutoTokenizer

model_id = "google/gemma-2b-it"

if torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"


tokenizer = lazy_object_proxy.Proxy(lambda: AutoTokenizer.from_pretrained(model_id))
model = lazy_object_proxy.Proxy(
    lambda: AutoModelForCausalLM.from_pretrained(model_id).to(device)
)
login_done = False


def ensure_login():
    """Makes sure that we're logged into HuggingFace Hub so that we can
    download the LLM (which requires to approve a license)."""

    global login_done

    if not login_done:
        login(token=environ["HUGGINGFACE_TOKEN"])
        login_done = True


def ask_gemma(instruction: str, this_input: str, max_tokens: int = 1000) -> str:
    ensure_login()

    chat = [
        {
            "role": "user",
            "content": f"# Instructions\n{instruction}\n# Input\n{this_input}",
        },
    ]

    prompt = tokenizer.apply_chat_template(
        chat,
        tokenize=False,
        add_generation_prompt=True,
    )
    inputs = tokenizer.encode(
        prompt,
        add_special_tokens=True,
        return_tensors="pt",
    )
    outputs = model.generate(
        input_ids=inputs.to(model.device),
        max_new_tokens=max_tokens,
    )

    convo_raw = tokenizer.decode(outputs[0])
    convo: Sequence[Dict] = parser.parse(convo_raw)  # noqa

    return convo[-1]["content"]


grammar = """
?start: bos* blocks eos

blocks: block*
block: start_of_turn role NL content end_of_turn?
bos: "<bos>"
eos: "<eos>"
start_of_turn: "<start_of_turn>"
end_of_turn: "<end_of_turn>"
role: role_user | role_model
role_user: "user"
role_model: "model"
content: /(?s)(.+?)(?=<end_of_turn>|<start_of_turn>|<eos>)/

%import common.NEWLINE -> NL
%import common.WS

%ignore WS
"""


class ParseTransformer(Transformer):
    """Transforms the parsed output of the LLM into the same object structure
    that we put into it. Allows to read back the conversation basically."""

    def block(self, items):
        return {"role": items[1].children[0], "content": items[3].children[0].value}

    blocks = list

    def start(self, items):
        return items[-2]

    def role_user(self, items):
        return "user"

    def role_model(self, items):
        return "model"


parser = Lark(grammar, parser="lalr", transformer=ParseTransformer())
