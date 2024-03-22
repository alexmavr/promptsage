<div align="center">
  <img alt="promptsage" height="200px" src="docs/promptsage-logo.jpg">
</div>

# Promptsage
Promptsage is an LLM prompt builder, linter and sanitizer with built-in 
guardrails. Combine all components of your prompt into a compressed LLM-ready
payload. Apply fine-grained access control over the context, and prevent
unwanted behavior with filters. Compatible with langchain and all major
datastores, LLMs and gateways.

## Quick Install

With pip:

```
pip install promptsage
```
## Examples

```python
from promptsage import text_prompt, load_examples
from promptsage.sources import PDF, LangchainDocuments
from promptsage.filters import PromptInject, Anonymize, TrimTokens

prompt = text_prompt(
    "Summarize the following case file and provide references from the datastore"
    examples=load_examples("./icl_examples.json")
    sources=[
        PDF('case_file.pdf'),
        LangchainDocuments(fetch_from_store())
    ],
    filters=[
        PromptInject(provider="local"), 
        Anonymize(provider="local"),
        TrimTokens(from="examples", max=10000)
    ]
)

# Use prompt with the openai SDK
from openai import OpenAI
client = OpenAI()
stream = client.chat.completions.create(
    model="gpt-4",
    messages=prompt.to_openai_messages(),
)

# Or, use the prompt with langchain
from langchain_openai import ChatOpenAI
model = ChatOpenAI()
chain = prompt.to_langchain_messages() | model
chain.invoke()
```
### Access Control

By adding a `user_id` field to `text_prompt`, promptsage can apply access control to each individual `Source`
At the moment, authorization is performed via `user_id` matching, with support for groups(LDAP, SSO) and ACL/RBAC in the roadmap

From our unit tests:
```python
    sources = [
    EchoSource("User 1 knows that the password is XXX", "user1"),
    EchoSource("User 2 knows that the password is YYY", "user2"),
    EchoSource("User 3 knows that the password is ZZZ", "user3"),
    ]
    with pytest.raises(UnauthorizedError):
        text_prompt(
            "What do I know?"
            sources=sources,
            user_id="user2",
        )
```

Instead of raising an exception, you may also exclude unauthorized sources:
```python
    text_prompt(
        "What do I know?"
        sources=sources,
        user_id="user2",
        access_control_policy=AccessControlPolicy.skip_unauthorized,
    )
```

#### Datastores

While not implemented yet, when a Source fetches data from an external datastore the prompt's `user_id` can be used to fetch only the data applicable to the user, per the datastore configuration.

## Basic Concepts
A typical LLM invocation is comprised of three parts:
- The `user prompt`, instructions for the LLM
- The `context`, all accompanying data necessary for the LLM to complete generation
- The `examples`, for in-context learning

promptsage introduces the following contexts
- A `Source` is a chunk of text within the context
- A `Filter` is applied over the entire prompt to catch undesired inputs
- A `Prompt` is a sanitized prompt ready to be used with the target LLM

## Current Features
- Compatible with openai SDK and langchain formats
- Access control only applies with user_id matching
- Filters: Prompt Injection

## Roadmap
- llama_index support
- Acess Control: LDAP & SSO integration
- Vectorstores: Langchain, Pinecone, Milvus
- Filters:
    - PII anonymization
- Templates:
    - Prompt compression