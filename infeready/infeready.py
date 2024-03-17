from typing import List
from abc import ABC, abstractmethod
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
import jinja2

class Source():
    def content(self) -> str:
        pass

class EchoSource(Source):
    def __init__(self, data: str):
        self.data = data

    def content(self) -> str:
        return self.data

class Filter(ABC):
    @abstractmethod
    def filter(self, str_prompt: str) -> str:
        pass

class NoopFilter(Filter):
    def filter(self, str_prompt: str) -> str:
        return str_prompt

class Template(ABC):
    @abstractmethod
    def render(self, user_prompt, examples: List[str], source_content: List[str]) -> str:
        pass

class DefaultTemplate(Template):
    template = '''
    {{user_prompt}}
    {% if examples %}
    ==== Examples ====
    {% for example in examples %}
    {{ example }}
    {% endfor %}
    {% endif %}
    {% if sources %}
    ==== Sources ====
    {% for source in sources %}
    {{ source }}
    {% endfor %}
    {% endif %}
    '''

    def render(self, user_prompt, examples: List[str], source_content: List[str]) -> str:
        environment = jinja2.Environment(trim_blocks=True, lstrip_blocks=True)
        context = {
            "user_prompt": user_prompt,
            "examples": examples,
            "sources": source_content
        }
        template = environment.from_string(self.template)
        return template.render(**context)

class Prompt():
    def __init__(self, str_prompt: str, messages: List[dict] = []):
        self.str_prompt = str_prompt
        self.messages = messages, # Always represents past messages

    def __str__(self):
        return self.str_prompt
    
    def to_str(self):
        return str(self)

    def to_openai_messages(self):
        return self.messages + [{"role": "user", "message": self.str_prompt}]

    def to_langchain_document(self):
        return Document(self.str_prompt)

    def to_langchain_messages(self):
        res = []
        for message in self.messages:
            if message["role"] == "system":
                res.append(SystemMessage(message["content"]))
            elif message["role"] == "user":
                res.append(HumanMessage(message["content"]))
        return res

def messages_prompt(
    messages: List[dict],
    user_prompt: str = "", # If specified, will be used instead of the last item in messages
    examples: List[str] = [],
    sources: List[Source] = [],
    filters: List[Filter] = [],
    max_token_count: int = -1,
    template: Template = DefaultTemplate(),
):
    # When no user_prompt is provided, use the last message from the messages list
    skip_last_message = False
    if user_prompt == "":
        if len(messages) == 0:
            raise ValueError("No messages provided and no user_prompt provided")
        if "role" not in messages[-1]:
            raise ValueError("Last message does not have a role")
        if messages[-1]["role"] != "user":
            raise ValueError("Last message is not from the user")
        user_prompt = messages[-1]["message"]
        skip_last_message = True

    source_content = []
    for source in sources:
        source_content.append(source.content())

    str_prompt = template.render(user_prompt, examples, source_content)

    for filter in filters:
        # Raises FilterError if any filter fails
        str_prompt = filter.filter(str_prompt)

    if skip_last_message:
        messages = messages[:-1]
    
    return Prompt(str_prompt, messages)
