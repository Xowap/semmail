from semmail.ai.gemma import ask_gemma, parser


def test_parse_llm_output():
    email = """<bos><start_of_turn>user
foo<end_of_turn>
<start_of_turn>model
bar<end_of_turn>
<start_of_turn>user
baz
boo
blop
<eos>"""
    parsed = parser.parse(email)

    assert parsed == [
        {"role": "user", "content": "foo"},
        {"role": "model", "content": "bar"},
        {"role": "user", "content": "baz\nboo\nblop\n"},
    ]


def test_ask_gemma():
    prompt = (
        "I will tell you a number. You must reply with only this number. No "
        "sentence, no punctuation, just the number."
    )

    assert ask_gemma(prompt, "42") == "42"
