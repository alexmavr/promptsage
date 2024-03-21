from typing import List
from enum import Enum
from abc import ABC, abstractmethod
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import jinja2

class Source(ABC):
    @abstractmethod
    def content(self, user_id: None, skip_unauthorized: bool = False) -> str:
        pass

class EchoSource(Source):
    def __init__(self, data: str, user_id: str = None):
        self.data = data
        self.user_id = user_id

    def content(self, user_id: str = None, skip_unauthorized: bool = False) -> str:
        if user_id and self.user_id and user_id != self.user_id:
            raise UnauthorizedError()
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

class UnauthorizedError(Exception):
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
        self.messages = messages # Always represents past messages

    def __str__(self):
        return self.str_prompt
    
    def to_str(self):
        return str(self)

    def to_openai_messages(self):
        return self.messages + [{"role": "user", "content": self.str_prompt}]

    def to_langchain_document(self):
        return Document(self.str_prompt)

    def to_langchain_messages(self):
        res = []
        for message in self.messages:
            if type(message) != dict:
                raise ValueError("Message is not a dictionary: " + str(message))
            if message["role"] == "system":
                res.append(SystemMessage(message["content"]))
            elif message["role"] == "user":
                res.append(HumanMessage(message["content"]))
            elif message["role"] == "assistant":
                res.append(AIMessage(message["content"]))

        res.append(HumanMessage(self.str_prompt))
        return res

class AccessControlPolicy(Enum):
    enforce_all = 1
    skip_unauthorized = 2

def _build_prompt(
        user_prompt: str,
        messages: List[dict],
        examples: List[str],
        sources: List[Source],
        filters: List[Filter],
        template: Template,
        user_id: str,
        access_control_policy: str,
) -> str:
    source_content = []
    for source in sources:
        # check if the user has access to the source, raise UnauthorizedError if not
        try:
            source_content.append(source.content(user_id, skip_unauthorized=True))
        except UnauthorizedError:
            if access_control_policy == AccessControlPolicy.enforce_all:
                raise
            elif access_control_policy == AccessControlPolicy.skip_unauthorized:
                continue

    str_prompt = template.render(user_prompt, examples, source_content)

    for filter in filters:
        # Raises FilterError if any filter fails
        str_prompt = filter.filter(str_prompt)
    return str_prompt

def text_prompt(
    user_prompt: str, # If specified, will be used instead of the last item in messages
    examples: List[str] = [],
    sources: List[Source] = [],
    filters: List[Filter] = [],
    template: Template = DefaultTemplate(),
    user_id: str = None,
    access_control_policy: str = AccessControlPolicy.enforce_all,
) -> str:
    return Prompt(_build_prompt(
        user_prompt,
        [],
        examples,
        sources,
        filters,
        template,
        user_id,
        access_control_policy,
    ))

def messages_prompt(
    messages: List[dict],
    user_prompt: str = "", # If specified, will be used instead of the last item in messages
    examples: List[str] = [],
    sources: List[Source] = [],
    filters: List[Filter] = [],
    template: Template = DefaultTemplate(),
    user_id: str = None,
    access_control_policy: str = AccessControlPolicy.enforce_all,
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
        user_prompt = messages[-1]["content"]
        skip_last_message = True

    str_prompt = _build_prompt(
        user_prompt,
        messages,
        examples,
        sources,
        filters,
        template,
        user_id,
        access_control_policy,
    )

    if skip_last_message:
        messages = messages[:-1]

    return Prompt(str_prompt, messages)
