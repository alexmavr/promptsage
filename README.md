# infeready

Infeready helps you craft efficient LLM-ready prompts from smaller building
blocks. Add history, data sources, ICL examples, and apply filters such as prompt
injection scanning, PII redaction or access control over the entire input.

## Quick Install

With pip:

```
pip install infeready
```

## Examples
Example invocation showcasing varying sources and filters (not all of which may be implemented at the time)

```python
from infeready import user_prompt, SystemPrompt
from infeready.sources import PDF, GoogleDrive, LangchainDocuments
from infeready.filters import PromptInject, Anonymize, AccessControl

examples = infeready.load_examples("./icl_examples.json")

system = SystemPrompt("You are LawyerGPT, and must estimate the most likely judicial outcome for a user provided case. Consider all provided documents and respond concisely."}

prompt = user_prompt(
    "determine the most likely legal outcome for the provided case",
    history=[system],
    examples=examples,
    sources=[
        PDF('case_file.pdf'),
        GoogleDrive("credentials.json")
        LangchainDocuments(get_langchain_docs()) # DIY fetch from vectorstore
    ],
    filters=[PromptInject(provider="epoch"), Anonymize(provider="local")],
    max_token_count=10000
)

# We can use the prompt in any LLM or library format
from openai import OpenAI
client = OpenAI()
stream = client.chat.completions.create(
    model="gpt-4",
    messages=prompt.to_openai_messages(),
    stream=True,
)
```

Example invocation with the openai messages format

```python
from infeready import messages_prompt
from infeready.sources import PDF, GoogleDrive, FromDocuments
from infeready.filters import PromptInject, Anonymize, AccessControl

examples = infeready.load_examples("./icl_examples.json")

messages = [
    {
        "role": "system",
        "content": "You are LawyerGPT, and must estimate the most likely judicial outcome for a user provided case. Consider all provided documents and respond concisely."
    },
    {
        "role": "user",
        "content": "determine the most likely legal outcome for the provided case"
    }
]

prompt = messages_prompt(
    messages,
    examples=examples,
    sources=[
        PDF('case_file.pdf'),
        GoogleDrive("credentials.json")
        FromDocuments(get_langchain_docs()) # DIY fetch from vectorstore
    ],
    filters=[PromptInject(provider="epoch"), Anonymize(provider="local")],
    max_token_count=10000
)


# Use the prompt with langchain
from langchain_openai import ChatOpenAI

model = ChatOpenAI()
chain = prompt.to_langchain_messages() | model
chain.invoke()
```

## Features

- Unit test creation: test prompt creation consistently every time
- Security and privacy scanners
- Compatible with openai and langchain input formats
