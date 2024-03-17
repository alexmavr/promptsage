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
Example invocation showcasing varying sources and filters (not all of which may be implemented at the time) and using the openai messages format

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
