# SemMail

A demo API (do not use in prod) that showcases how you can leverage LLMs in
order to parse emails into machine-readable JSON.

## Installation

We recommend to use [uv](https://github.com/astral-sh/uv) as a package manager,
since it has advanced override features which often comes in handy in order to
navigate in the fuckfest that machine learning dependencies are. If `uv` is
installed, you should be able to get started with a:

```bash
make sync
```

> _Note_ &mdash; I'm assuming you have `uv` and `make` installed in a
> Linux/Mac-ish shell. If not, you will have to invent the procedure for
> yourself.

At this point you need to decide which LLM you want to run. You have two
choices:

-   `gemma` &mdash; Google's lightweight LLM (in the 2B version). It can run
    decently on a CPU but be careful because this will eat up 10 Gio of RAM
    immediately so **be prepared**.
-   `openai` &mdash; If you want to use GPT-4, which will definitely work much
    better and much faster than a CPU-powered Gemma. But you then all your datas
    are belong to OpenAI. Your choice.

Pick one and read the following section down below.

### Gemma

If you decide to go with Gemma, the first thing you need is a
[HuggingFace](https://huggingface.co/) account from which you will go into the
settings and get yourself a nice API token.

Then you'll have to visit the
[model's page](https://huggingface.co/google/gemma-2b-it) and accept the license
of the model. Otherwise you won't be able to download it.

Just to be clear, Gemma is entirely free and runs entirely on your machine. It's
just leaning on HuggingFace to download the huge weight files that it needs to
run.

When you're done, put in your `.env` file (replace the `xxx`):

```bash
HUGGINGFACE_TOKEN=xxx
```

> _Note_ &mdash; If you have CUDA, it should enable itself automatically and you
> should get an accelerated performance. This is written in conditional tense
> because I don't have CUDA so I couldn't test.

### OpenAI

A safe and popular choice would be to go with OpenAI. In which case you need
also to create an account to [their platform](https://platform.openai.com/), put
your credit card and get yourself an API key.

When it's done, just put in your `.env` file (replace the `xxx`):

```bash
SEMMAIL_LLM=openai
OPENAI_API_KEY=xxx
```

## Run the project

Then to run the project, which is a regular Flask project, just:

```bash
make serve
```

At this point you can visit http://localhost:5000 and see a beautiful design.
