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
from infeready.sources import PDF, GoogleDrive, LangchainDocuments
from infeready.filters import PromptInject, Anonymize, TrimTokens

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
        LangchainDocuments(get_langchain_docs()) # DIY fetch from vectorstore
    ],
    filters=[
        PromptInject(provider="local"), 
        Anonymize(provider="local"),
        TrimTokens(from="examples", max=10000)
    ]
)

# Use the prompt with langchain
from langchain_openai import ChatOpenAI

model = ChatOpenAI()
chain = prompt.to_langchain_messages() | model
chain.invoke()

# Or, use prompt with the openai SDK
from openai import OpenAI
client = OpenAI()
stream = client.chat.completions.create(
    model="gpt-4",
    messages=prompt.to_openai_messages(),
)
```

## Current Features
- Compatible with openai and langchain input formats

## Roadmap
- Filters:
    - Prompt Injection
    - PII redaction
    - Access Control (applicable per data source item)
    - Prompt compression:
        - Remove repeated content in examples
        - Minimum Viable Template
- Sources:
    - PDF, GoogleDrive ... (file an issue to ask for a source!)
- Unit test utils: Assertions for prompts without string matching